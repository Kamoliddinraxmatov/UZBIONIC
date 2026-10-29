"""AC-2: generator is deterministic and its ground truth matches the burst schedule."""

import numpy as np

from simulation.signal import Burst, generate_emg

FS = 2000.0


def test_same_seed_same_output():
    kw = dict(duration_s=5.0, fs=FS, bursts=[Burst(1.0, 1.0, 0.5)], mains_amp=0.05)
    a = generate_emg(seed=3, **kw)
    b = generate_emg(seed=3, **kw)
    assert np.array_equal(a.x, b.x)


def test_different_seed_different_output():
    a = generate_emg(5.0, FS, seed=3)
    b = generate_emg(5.0, FS, seed=4)
    assert not np.array_equal(a.x, b.x)


def test_ground_truth_mask():
    rec = generate_emg(5.0, FS, [Burst(1.0, 1.5, 0.5)], seed=0)
    assert rec.active.sum() == int(1.5 * FS)
    assert rec.active[int(1.2 * FS)] and not rec.active[int(0.9 * FS)]


def test_burst_raises_rms():
    rec = generate_emg(5.0, FS, [Burst(2.0, 2.0, 0.5)], rest_rms=0.05, seed=0)
    rest = rec.x[: int(1.5 * FS)]
    burst = rec.x[int(2.5 * FS) : int(3.5 * FS)]
    assert np.sqrt(np.mean(burst**2)) > 5 * np.sqrt(np.mean(rest**2))
