# Requirements — UZBIONIC (DRAFT v0.1)

Conventions: `SHALL` = mandatory, `SHOULD` = goal. Every numeric value is either `TBD` or marked
with its source. Values tagged *(assumption)* come from general sEMG engineering practice and
must be confirmed against literature/datasheets before they drive hardware selection.

Verification methods: **T** test, **A** analysis, **I** inspection, **D** demonstration.

## Safety (SAF)
| ID | Requirement | Verif. |
|---|---|---|
| SAF-01 | The project SHALL NOT perform human-use testing until a documented ethics/safety review is approved by the owner. | I |
| SAF-02 | The system SHALL be non-invasive; no component penetrates skin. | I |
| SAF-03 | Every actuator SHALL have a hardware or firmware current/torque limit. Value TBD. | T |
| SAF-04 | The system SHALL enter a defined safe state within TBD ms after EMG signal loss, controller fault, or E-stop. | T |
| SAF-05 | A physical emergency stop SHALL cut actuator power on the bench prototype. | T |
| SAF-06 | Any future body-contact electronics SHALL be electrically isolated from mains-powered equipment (standard to be identified, e.g. IEC 60601 family — to research, not claimed). | A |

## EMG acquisition (EMG)
| ID | Requirement | Verif. |
|---|---|---|
| EMG-01 | Number of sEMG channels: TBD (start: 1–2 for MVP). | I |
| EMG-02 | Signal bandwidth SHALL cover approx. 20–450 Hz *(assumption)*. | A/T |
| EMG-03 | Sampling rate SHALL be ≥ 1 kHz per channel *(assumption)*. | T |
| EMG-04 | Mains interference (50 Hz in Uzbekistan) SHALL be attenuated; method TBD. | T |
| EMG-05 | The acquisition chain SHALL accept a bench test signal (signal generator / DAC replay) in place of electrodes. | D |

## Signal processing & control (SP)
| ID | Requirement | Verif. |
|---|---|---|
| SP-01 | Pipeline: filtering → envelope/features → decision → grip command. | I |
| SP-02 | End-to-end latency (signal onset → motor command) SHALL be ≤ TBD ms (literature target to cite). | T |
| SP-03 | MVP control: on/off (open/close) by envelope threshold with hysteresis. | T |
| SP-04 | Pipeline SHALL produce identical results in Python (reference) and firmware within a stated tolerance. | T |
| SP-05 | False activation rate on rest-signal recordings ≤ TBD per minute. | T |

## Mechanical (MEC)
| ID | Requirement | Verif. |
|---|---|---|
| MEC-01 | Degrees of freedom / number of actuators: TBD (D-04). | I |
| MEC-02 | Grip force target: TBD with cited source. | T |
| MEC-03 | Total hand mass target: TBD with cited source. | T |
| MEC-04 | Open→close time: TBD. | T |
| MEC-05 | Mechanical end-stops SHALL prevent over-travel independent of firmware. | T |

## Electronics & power (ELE)
| ID | Requirement | Verif. |
|---|---|---|
| ELE-01 | Bench prototype SHALL run from a current-limited lab supply; battery is out of MVP scope. | I |
| ELE-02 | Motor driver SHALL report or allow measurement of motor current. | T |
| ELE-03 | Debug interface: UART/USB telemetry of raw signal, envelope, state, command. | D |

## Firmware (FW)
| ID | Requirement | Verif. |
|---|---|---|
| FW-01 | Core logic SHALL be hardware-independent and unit-testable on a PC. | T |
| FW-02 | Fixed-rate control loop; rate TBD (≥ processing window rate). | T |
| FW-03 | Watchdog SHALL trigger safe state on firmware hang. | T |

## Documentation & process (DOC)
| ID | Requirement | Verif. |
|---|---|---|
| DOC-01 | Every hardware parameter in docs SHALL cite a datasheet or measurement. | I |
| DOC-02 | Every cost SHALL cite a dated quote. | I |
| DOC-03 | Significant decisions SHALL be recorded as ADRs. | I |
