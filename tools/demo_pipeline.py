"""Plot synthetic EMG -> filtered signal -> envelope + thresholds -> detection -> grip command.

Usage: python tools/demo_pipeline.py [output.png]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from emg.pipeline import Command, GripStateMachine, calibrate_thresholds, process
from simulation.signal import Burst, generate_emg

FS = 2000.0


def main(out: str = "demo_pipeline.png") -> None:
    rest = generate_emg(20.0, FS, rest_rms=0.05, mains_amp=0.05, seed=101)
    _, rest_env, _ = process(rest.x, FS, None)
    thr = calibrate_thresholds(rest_env[int(0.5 * FS):])

    bursts = [Burst(1.0, 1.2, 0.4), Burst(4.0, 0.6, 0.25), Burst(6.0, 2.0, 0.5)]
    rec = generate_emg(10.0, FS, bursts, rest_rms=0.05, mains_amp=0.05, seed=7)
    y, env, active = process(rec.x, FS, thr)

    sm = GripStateMachine()
    cmd = np.array([sm.step(bool(a)).value for a in active])
    level = {Command.OPEN.value: -1, Command.STOP.value: 0, Command.CLOSE.value: 1, Command.SAFE_STOP.value: 0}

    fig, ax = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    ax[0].plot(rec.t, rec.x, lw=0.4)
    ax[0].set_ylabel("raw (a.u.)")
    ax[1].plot(rec.t, y, lw=0.4)
    ax[1].set_ylabel("filtered")
    ax[2].plot(rec.t, env, label="envelope")
    ax[2].axhline(thr.on, color="r", ls="--", label="on")
    ax[2].axhline(thr.off, color="g", ls="--", label="off")
    ax[2].legend(loc="upper right")
    ax[2].set_ylabel("RMS")
    ax[3].fill_between(rec.t, 0, rec.active, step="post", alpha=0.3, label="true burst")
    ax[3].step(rec.t, active, where="post", label="detected")
    ax[3].step(rec.t, [level[c] for c in cmd], where="post", label="command (-1 open, 1 close)")
    ax[3].legend(loc="upper right")
    ax[3].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
