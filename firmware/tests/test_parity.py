"""Firmware C core vs Python reference on the same synthetic two-site signals (SP-04).

Builds the C harness with the system C compiler; skipped if none is installed.
"""

import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from emg.pipeline import calibrate_thresholds, onsets, process, process_two_site
from simulation.signal import Burst, generate_emg

FS = 2000.0
FW = Path(__file__).resolve().parents[1]
CMD_CODE = {"stop": 0, "open": 1, "close": 2, "safe_stop": 3}


@pytest.fixture(scope="module")
def host_run(tmp_path_factory):
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        pytest.skip("no C compiler")
    exe = tmp_path_factory.mktemp("fw") / "host_run"
    srcs = [FW / "tests/host_run.c", FW / "src/uzb_dsp.c", FW / "src/uzb_control.c"]
    subprocess.run(
        [cc, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-I", str(FW / "include"), *map(str, srcs), "-o", str(exe), "-lm"],
        check=True,
    )
    return exe


def _thr(seed):
    rest = generate_emg(30.0, FS, rest_rms=0.05, mains_amp=0.05, seed=seed)
    _, env, _ = process(rest.x, FS, None)
    return calibrate_thresholds(env[int(0.5 * FS):])


def test_c_matches_python(host_run):
    b = generate_emg(20.0, FS, [Burst(1.0, 1.0, 0.4), Burst(8.0, 2.0, 0.3), Burst(14.0, 1.0, 0.4)], mains_amp=0.05, seed=21)
    t = generate_emg(20.0, FS, [Burst(4.0, 1.0, 0.4), Burst(11.0, 1.5, 0.25), Burst(14.0, 1.0, 0.4)], mains_amp=0.05, seed=22)
    close_x, open_x = b.x + 0.1 * t.x, t.x + 0.1 * b.x
    ct, ot = _thr(101), _thr(102)

    ce, oe, ca, oa, cmds = process_two_site(close_x, open_x, FS, ct, ot)

    stdin = "\n".join(f"{c:.9g},{o:.9g}" for c, o in zip(close_x, open_x)) + "\n"
    out = subprocess.run(
        [str(host_run), repr(ct.on), repr(ct.off), repr(ot.on), repr(ot.off)],
        input=stdin, capture_output=True, text=True, check=True,
    ).stdout
    fw = np.loadtxt(out.splitlines(), delimiter=",")
    assert fw.shape == (len(close_x), 5)

    # float32 firmware vs float64 reference
    np.testing.assert_allclose(fw[:, 0], ce, rtol=1e-3, atol=1e-4)
    np.testing.assert_allclose(fw[:, 1], oe, rtol=1e-3, atol=1e-4)

    # same activations, allowing a couple of samples' shift at each threshold crossing
    for col, ref in ((2, ca), (3, oa)):
        got = fw[:, col].astype(bool)
        assert len(onsets(got)) == len(onsets(ref))
        assert np.max(np.abs(onsets(got) - onsets(ref))) <= 2
        assert np.mean(got != ref) < 1e-3

    ref_cmd = np.array([CMD_CODE[c.value] for c in cmds])
    assert np.mean(fw[:, 4] != ref_cmd) < 1e-3
