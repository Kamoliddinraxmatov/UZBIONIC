# Development Roadmap — UZBIONIC (DRAFT v0.1)

Durations are intentionally omitted until team size and budget are known (D-01).
Each milestone ends with a gate review by the owner.

The full plan to a first wearable prototype (phases 0–10: competitor analysis, software,
electronics, 3D design, purchasing, printing/assembly, bench tests, safety gate, first wearing) is
kept in the project's master plan document. M0–M5 below are the engineering milestones inside it.

| Milestone | Goal | Hardware needed | Gate |
|---|---|---|---|
| **M0** Foundation & offline pipeline | Repo, docs, Python reference EMG pipeline on synthetic data, tests | None (PC only) | Acceptance criteria in `07-milestone-M0.md` |
| **M1** Simulation & HIL-on-PC | Kinematic finger model + state machine driven by replayed EMG (synthetic + public datasets) | None | Latency/false-activation analysis; decisions D-02..D-05 drafted |
| **M2** Hardware selection | Candidate tables from datasheets; real quotes; ADRs | None purchased yet | **Owner approves purchase list** |
| **M3** Bench electronics | Signal generator/DAC → AFE → MCU → telemetry; firmware DSP matches Python | Dev board, AFE module, signal source | Measured bandwidth, sampling, latency vs requirements |
| **M4** Single-finger bench rig | MCU drives one actuated finger on a test jig with E-stop and current limit | Actuator, driver, printed finger, jig | Open/close cycles, force & time measured, safe-state tests |
| **M5** Multi-finger bench hand | Full hand mechanism on jig, multiple grips | TBD | Endurance cycles, documented results |
| M6 | Wearable prototype: socket from a specific user's measurements, battery, enclosure | TBD | Safety gate (charter 3a) passed before first wearing |
