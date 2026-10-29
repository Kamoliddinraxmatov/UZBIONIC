# Minimum Viable Bench Prototype (DRAFT v0.1)

## 1. Definition
**One EMG channel controls one actuated finger on a test jig, open/close, with no person involved.**
The EMG input comes from a bench signal source (function generator or DAC replaying recorded
or synthetic sEMG), never from electrodes on a person.

It proves: acquisition → processing → decision → actuation → feedback → safe state, end to end,
with measurable latency and false-activation behaviour.

## 2. Components (functional, no part numbers yet)
| # | Function | Selection status |
|---|---|---|
| 1 | Bench EMG signal source (generator or DAC replay) | Open (D-06) |
| 2 | sEMG analog front end (1 ch) | Open (D-02) |
| 3 | Microcontroller dev board with ADC ≥ needed resolution/rate | Open (D-03) |
| 4 | Motor driver with current limit / current sense | Open (D-04) |
| 5 | Actuator (e.g. small geared DC motor or servo — topology TBD) | Open (D-04) |
| 6 | Position feedback (potentiometer or encoder) | Open |
| 7 | 3D-printed finger + test jig with end-stops | Open (D-09, D-10) |
| 8 | Current-limited lab supply + hardware E-stop | Open |
| 9 | PC with logging/visualization tool | Available (assumed) |

## 3. Interfaces
| ID | From → To | Type | Parameters |
|---|---|---|---|
| IF-01 | Signal source → AFE input | Analog, differential or single-ended (TBD) | Amplitude range TBD, must match AFE input range; bandwidth per EMG-02 |
| IF-02 | AFE output → MCU ADC | Analog, single-ended | Output range must fit ADC reference (TBD from datasheets) |
| IF-03 | MCU → motor driver | PWM + DIR (or servo PWM) + ENABLE | Frequency TBD from driver datasheet |
| IF-04 | Sensors → MCU | Analog (pot, current sense) or digital (encoder) | TBD |
| IF-05 | MCU ↔ PC | UART over USB, text/CSV or binary frames | Fields: timestamp, raw, filtered, envelope, state, command, current, position |
| IF-06 | Motor → finger | Tendon or linkage | TBD (D-04) |
| IF-07 | Finger → jig | Mechanical mount, end-stops, optional force sensor | TBD |
| IF-08 | E-stop → driver power | Hardware cut, independent of MCU | — |

## 4. Software interfaces (proposed, to be fixed in M0/M1)
```python
# emg/pipeline (reference)
filter_signal(x: ndarray, fs: float, cfg) -> ndarray
envelope(x: ndarray, fs: float, window_ms: float) -> ndarray
detect(env: ndarray, on_thr, off_thr, min_ms, fs) -> ndarray[bool]   # hysteresis
GripStateMachine.step(active: bool, fault: bool) -> Command          # OPEN/CLOSE/HOLD/SAFE
```
Firmware `dsp/` and `app/` mirror these signatures in C.

## 5. Bench verification (outline)
- Inject known bursts → measure onset-to-command latency.
- Inject rest-level noise for N minutes → count false activations.
- Disconnect signal / press E-stop → verify SAFE within SAF-04 limit.
- Stall finger at end-stop → verify current limit holds.
