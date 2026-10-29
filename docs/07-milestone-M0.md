# Milestone M0 — Foundation & Offline EMG Pipeline (DRAFT v0.1)

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
| AC-3 | Band-pass filter attenuates a 5 Hz and a 1 kHz test sine by ≥ 20 dB and passes a 100 Hz sine within ±3 dB (fs = 2 kHz in test) | Unit test |
| AC-4 | With notch enabled, injected 50 Hz component reduced by ≥ 20 dB | Unit test |
| AC-5 | On synthetic data with 20 known bursts, detector finds 20/20 with onset error ≤ 100 ms (algorithmic, not system latency) | Unit test |
| AC-6 | On 60 s of synthetic rest signal, 0 false activations | Unit test |
| AC-7 | State machine: any fault input → SAFE; SAFE exits only on reset | Unit tests covering all transitions |
| AC-8 | `pytest` passes from a clean checkout with one documented install command | Demonstration |
| AC-9 | No hardware numbers in code/docs without citation or `TBD` | Inspection |

Note: thresholds in AC-3..AC-6 are test-design values for synthetic data, not product requirements.

## Out of scope for M0
Firmware, real EMG data, hardware, CAD.

## Estimated size
Roughly 300–500 lines of Python + tests. Starts **only after owner approval**.
