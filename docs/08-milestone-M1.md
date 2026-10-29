# Milestone M1 — Two-site control and firmware core (v0.1, 2026-10-29)

**Why:** the first user has a left transhumeral (above-elbow) amputation, so the hand is driven by
two EMG sites: biceps closes, triceps opens. This milestone adds that control in the Python reference
and ports the whole per-sample chain to hardware-independent C for the microcontroller.

## Scope
- `emg/pipeline/two_site.py` — intent from two channels; controller: CLOSE / OPEN / STOP; rest and
  co-contraction stop; end-of-travel limits stop; any fault latches SAFE until reset.
- `firmware/` — C11 core, no MCU headers: biquad filters (coefficients generated from the Python
  design by `tools/gen_fw_coeffs.py`), moving RMS, hysteresis detector, two-site controller;
  PC harness `tests/host_run.c`; C unit tests; CMake build.
- `emg/pipeline/modes.py` + `firmware/src/uzb_modes.c` — requirement from 2026-10-29: the hand should
  move like human fingers and a wrist. A short co-contraction (50–800 ms, both muscles, then release)
  steps POWER (all fingers) → PINCH (thumb + index) → POINT (all but index) → WRIST (rotation) → POWER.
  A 300 ms lockout after each switch keeps uneven relaxation from starting a movement. Timings are
  tunable design values, to be adjusted with the user and a prosthetist. Actuator layout assumed:
  5 finger motors + 1 wrist-rotation motor (decision D-04 still open).
- `firmware/tests/test_parity.py` — runs the C core and the Python reference on the same two-site
  signals and compares them (requirement SP-04).

## Acceptance criteria
| # | Criterion | Result |
|---|---|---|
| M1-1 | Biceps burst → CLOSE, triceps burst → OPEN, rest and co-contraction → STOP, with 10 % crosstalk between sites | Pass (`emg/tests/test_two_site.py`) |
| M1-2 | Fault → SAFE, latched until reset (Python and C) | Pass |
| M1-3 | C envelope within 0.1 % (rel) of Python | Pass — measured max 0.003 % |
| M1-4 | C activations: same onset count, onsets within 2 samples, < 0.1 % differing samples | Pass — measured 0 differing samples |
| M1-5 | C builds with `-Wall -Wextra -Werror` | Pass |
| M1-6 | Short co-contraction steps the mode, too short/too long does not, lockout after switch, no switching in SAFE (Python and C) | Pass |
| M1-7 | C and Python give the same mode sequence on the same signals | Pass |

## Not covered yet
- MCU-specific HAL (ADC sampling, PWM, timers) — waits for the MCU decision (D-03).
- Real sEMG data; electrode placement on biceps/triceps is for the prosthetist to decide.
- The running RMS sum uses `double`; to revisit if the chosen MCU has no double-precision FPU.
