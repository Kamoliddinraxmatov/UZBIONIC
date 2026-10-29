# Unknowns, Assumptions, Decisions (DRAFT v0.1)

## A. Decisions required before hardware selection
| ID | Decision | Options (not exhaustive) | Needed by |
|---|---|---|---|
| D-01 | Budget and team/time available | — | M2 |
| D-02 | sEMG front end: ready-made module vs custom AFE | module (fast) / custom (control, learning) | M2 |
| D-03 | MCU family & toolchain | to compare by ADC, DSP capability, toolchain, local availability | M2 |
| D-04 | Actuation topology & number of actuators | per-finger motors / tendon-driven underactuated / servos | M2 |
| D-05 | Control scheme for later phases | threshold on/off → proportional → pattern recognition | M1 |
| D-06 | Bench EMG source | lab function generator / DAC replay from dataset | M2 |
| D-07 | Safe-state behaviour on fault | open / hold / freeze | M1 |
| D-08 | Target user profile (hand side, size, amputation level) for future design | — | M2 (for mechanics sizing) |
| D-09 | Manufacturing access: 3D printer type & material, PCB fab | — | M2 |
| D-10 | CAD tool & source format | — | M1 |
| D-11 | Public sEMG datasets to use (licence check) | — | M1 |
| D-12 | Repository licence and visibility (open vs closed) | — | Before first commit |
| D-13 | Where the Git repository will live | **Decided:** github.com/Kamoliddinraxmatov/UZBIONIC | Done |
| D-14 | Open or closed design | **Decided 2026-10-29:** open, own design from scratch (see charter 3b); exact licence still open | Before first public release |

## B. Major unknowns
- Real sEMG amplitude/noise at the intended muscle sites and electrode types (to come from literature/datasets, not guesses).
- Required grip force, speed and hand mass for useful function (needs cited sources / prosthetist input).
- Local availability, lead time and real price of candidate components in Uzbekistan.
- Applicable regulatory pathway in Uzbekistan and target markets (research only).
- Who provides medical/ethics oversight before any future human involvement.

## C. Working assumptions (to be verified, each can be overturned)
- A1: sEMG useful band ≈ 20–450 Hz; sampling ≥ 1 kHz is adequate. *(general practice, cite in M1)*
- A2: Mains frequency is 50 Hz.
- A3: One channel + threshold control is sufficient to prove the chain end-to-end.
- A4: Development PC with Python 3 is available.
- A5: A dev board + modules is cheaper and faster than a custom PCB for M3–M4.
- A6: Replay of recorded/synthetic EMG is acceptable as the bench input; no electrodes on people.
