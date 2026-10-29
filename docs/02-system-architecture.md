# System Architecture — UZBIONIC (DRAFT v0.1)

## 1. Block diagram (logical, hardware-agnostic)

```
 [Signal source]          [Acquisition]            [Controller MCU]                    [Actuation]
  bench: sig-gen /  ──►  analog front end  ──►  ADC → DSP pipeline → state machine ──►  motor driver ──► motor ──► finger/tendon
  DAC replay              (gain, filters)        (filter, envelope,   (OPEN/CLOSE/       (current limit)            │
  future: electrodes                              threshold)            HOLD/SAFE)                                  ▼
                                                        │   ▲                                              [Sensors]
                                                        │   └──────── position / current feedback ◄──── encoder/pot, current sense
                                                        ▼
                                                 [Telemetry UART/USB] ──► PC logger / visualizer
                    [E-stop] ──► cuts actuator power (hardware path, independent of MCU)
```

## 2. Subsystems
| Subsystem | Responsibility | Key interfaces |
|---|---|---|
| Signal source | Provide repeatable EMG-like signals on the bench | Analog out → AFE input (IF-01) |
| Analog front end (AFE) | Amplify and band-limit sEMG | Analog → ADC (IF-02) |
| Controller | Sampling, DSP, control state machine, safety | ADC, PWM/driver (IF-03), feedback (IF-04), telemetry (IF-05) |
| Actuation | Convert command to finger motion | Driver → motor → mechanism (IF-06) |
| Mechanics | Finger(s), tendon/linkage, end-stops, mounting on test jig | IF-06, IF-07 (jig) |
| PC tools | Reference pipeline, simulation, logging, analysis | IF-05 |

## 3. Software layering (firmware)
```
app/        state machine, grip logic
dsp/        filters, envelope, threshold — pure C, host-testable (mirrors emg/pipeline in Python)
safety/     watchdog, fault monitor, safe-state
hal/        ADC, PWM, GPIO, UART — only layer that touches the MCU
```
The Python pipeline in `emg/pipeline` is the **reference implementation**; firmware DSP is
tested against it using shared test vectors (SP-04).

## 4. Control state machine (MVP)
`INIT → IDLE(open) ⇄ CLOSING → HOLD → OPENING → IDLE`; any state → `SAFE` on fault/E-stop/signal
loss. Exit from `SAFE` only by explicit reset.

## 5. Open architecture decisions
See `06-unknowns-assumptions-decisions.md` (D-02 AFE: module vs custom, D-03 MCU family,
D-04 actuator topology, D-07 safe-state behaviour).
