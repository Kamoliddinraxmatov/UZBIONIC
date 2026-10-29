# Milestone M0 — Foundation & Offline EMG Pipeline (v0.2)

**Goal:** a small, PC-only, fully testable step. No hardware, no purchases, no people.

## Scope
1. Create the repository with the approved structure and these docs.
2. `simulation/signal/`: synthetic sEMG generator — rest noise + activation bursts
   (band-limited noise, amplitude-modulated), plus optional 50 Hz interference; seeded, reproducible.
3. `emg/pipeline/`: band-pass filter, optional 50 Hz notch, rectification + moving RMS envelope,
   hysteresis threshold detector with minimum duration.
4. `emg/pipeline/state_machine.py`: OPEN/CLOSE/HOLD/SAFE logic.
5. `emg/tests/`: pytest suite; a script that plots signal → envelope → state.

## Acceptance criteria (all must pass)
| # | Criterion | How verified |
|---|---|---|
| AC-1 | Repo structure matches approved README; all docs present | Inspection |
| AC-2 | Generator is deterministic: same seed → identical output | Unit test |
| AC-3 | Band-pass filter attenuates a 5 Hz and a 900 Hz test sine (1 kHz is the Nyquist frequency at fs = 2 kHz, so 900 Hz is used) by ≥ 20 dB and passes a 100 Hz sine within ±3 dB (fs = 2 kHz in test) | Unit test |
| AC-4 | With notch enabled, injected 50 Hz component reduced by ≥ 20 dB | Unit test |
| AC-5 | On synthetic data with 20 known bursts, detector finds 20/20 with onset error ≤ 100 ms (algorithmic, not system latency) | Unit test |
| AC-6 | On 60 s of synthetic rest signal, 0 false activations | Unit test |
| AC-7 | State machine: any fault input → SAFE; SAFE exits only on reset | Unit tests covering all transitions |
| AC-8 | `pytest` passes from a clean checkout with one documented install command | Demonstration |
| AC-9 | No hardware numbers in code/docs without citation or `TBD` | Inspection |

Note: thresholds in AC-3..AC-6 are test-design values for synthetic data, not product requirements.

## Results (2026-10-29)
`pytest`: 30 passed. Implemented in `simulation/signal/`, `emg/pipeline/`, `emg/tests/`, `simulation/tests/`.

- Filters are causal (sample-by-sample, like firmware): 4th-order Butterworth 20–450 Hz + 50 Hz notch (Q = 30).
- Envelope: causal moving RMS, 50 ms window. Detector: on/off hysteresis, 30 ms min-on, 100 ms min-off;
  thresholds = 4× / 2.5× median rest envelope, calibrated on a separate rest recording.
- AC-5: 20/20 bursts detected; onset delay 55–69 ms (mean 61 ms) on synthetic data. Includes the 30 ms
  burst ramp of the generator; this is algorithmic delay only, not system latency.
- AC-6: 0 false activations in 60 s rest (also 0 in a 10 × 60 s extra check with other seeds).
- First tried 100 ms window / 50 ms min-on: onset delay up to 108 ms, failing AC-5, so the window was shortened.
- Limits: synthetic data only. No real sEMG, no fatigue, crosstalk or motion artefacts yet (risk R-04).

## Out of scope for M0
Firmware, real EMG data, hardware, CAD.

## Estimated size
Roughly 300–500 lines of Python + tests. Starts **only after owner approval**.
