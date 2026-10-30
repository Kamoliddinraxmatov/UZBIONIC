"""Print the R1/R2 synthetic benchmark table used in docs/16-pattern-recognition-R1.md.

    python -m simulation.patrec_demo

Numbers come from synthetic data only. They show how the code behaves (limb position
effect, rejection, voting, channel count), not how accurate a real user will be.
"""

from __future__ import annotations

import numpy as np

from emg.patrec import PatternRecognizer, PositionAwareRecognizer, RecognizerConfig, REST, window_labels
from simulation.signal import generate_session, make_arm_model, training_protocol

FS = 1000.0
SEEDS = (1, 2, 3, 4, 5)


def score(decisions, ends, labels, w):
    y = window_labels(labels, ends, w)
    k = y >= 0
    d, y = decisions[k], y[k]
    acc = float(np.mean(d == y))
    moving = d != REST
    err_moving = float(np.mean(d[moving] != y[moving])) if moving.any() else 0.0
    flips = int(np.sum(d[1:] != d[:-1]))
    return acc, err_moving, flips


def sessions(model, seed):
    all_pos = tuple(range(model.n_positions))
    tr0 = generate_session(model, training_protocol(model, (0,), reps=2), FS, seed=seed * 10 + 1)
    tra = generate_session(model, training_protocol(model, all_pos, reps=2), FS, seed=seed * 10 + 2)
    te = generate_session(model, training_protocol(model, all_pos, reps=1, hold_s=4.0), FS, seed=seed * 10 + 3)
    return tr0, tra, te


def position_table():
    rows = {"train arm-down only": [], "train all positions": [], "all positions + accelerometer (2-stage)": []}
    for s in SEEDS:
        m = make_arm_model(seed=s)
        tr0, tra, te = sessions(m, s)
        rows["train arm-down only"].append(score(*PatternRecognizer().fit(tr0.emg, tr0.labels, FS).predict(te.emg, FS), te.labels, 200)[0])
        rows["train all positions"].append(score(*PatternRecognizer().fit(tra.emg, tra.labels, FS).predict(te.emg, FS), te.labels, 200)[0])
        pa = PositionAwareRecognizer().fit(tra.emg, tra.labels, tra.positions, tra.acc, FS)
        rows["all positions + accelerometer (2-stage)"].append(score(*pa.predict(te.emg, te.acc, FS), te.labels, 200)[0])
    return {k: float(np.mean(v)) for k, v in rows.items()}


def channel_table(channels=(2, 4, 8)):
    out = {}
    for ch in channels:
        accs = []
        for s in SEEDS:
            m = make_arm_model(n_channels=ch, seed=s)
            _, tra, te = sessions(m, s)
            accs.append(score(*PatternRecognizer().fit(tra.emg, tra.labels, FS).predict(te.emg, FS), te.labels, 200)[0])
        out[ch] = float(np.mean(accs))
    return out


def safety_table(ch=4):
    cfgs = {
        "plain": RecognizerConfig(),
        "rejection 0.9": RecognizerConfig(reject_below=0.9),
        "rejection 0.9 + vote 5": RecognizerConfig(reject_below=0.9, vote=5),
    }
    out = {}
    for name, cfg in cfgs.items():
        res = []
        for s in SEEDS:
            m = make_arm_model(n_channels=ch, seed=s)
            _, tra, te = sessions(m, s)
            res.append(score(*PatternRecognizer(cfg).fit(tra.emg, tra.labels, FS).predict(te.emg, FS), te.labels, 200))
        out[name] = tuple(float(np.mean([r[i] for r in res])) for i in range(3))
    return out


def main():
    print("Limb position effect (8 channels, 5 classes, 3 arm positions), accuracy:")
    for k, v in position_table().items():
        print(f"  {k:42s} {v:6.1%}")
    print("Channel count (trained in all positions), accuracy:")
    for k, v in channel_table().items():
        print(f"  {k} channels {v:6.1%}")
    print("Safety (4 channels): accuracy / wrong-motion rate when moving / class flips:")
    for k, (a, e, f) in safety_table().items():
        print(f"  {k:24s} {a:6.1%}  {e:6.1%}  {f:5.0f}")


if __name__ == "__main__":
    main()
