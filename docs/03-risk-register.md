# Risk Register — UZBIONIC (DRAFT v0.1)

Scale: Likelihood (L) and Impact (I) 1–5; Score = L×I. Ratings are initial judgments, to be reviewed.

| ID | Risk | L | I | Score | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-01 | Pressure to test on a person before safety/ethics review | 3 | 5 | 15 | SAF-01 gate; bench-only signal sources; written review before any change | Owner |
| R-02 | Electrical hazard if body-contact electronics later connect to mains-powered PC | 2 | 5 | 10 | Isolation requirement SAF-06; battery-powered or isolated USB for any future contact | Eng |
| R-03 | Requirements built on unverified numbers | 4 | 4 | 16 | DOC-01; `TBD` until cited; literature review task | Eng |
| R-04 | Synthetic EMG not representative of real sEMG (noise, crosstalk, fatigue) | 4 | 3 | 12 | Use licensed public sEMG datasets for replay; document limits | Eng |
| R-05 | Actuator too weak / too slow / too heavy | 3 | 4 | 12 | Measure on bench before committing; candidate comparison table | Eng |
| R-06 | Mechanical pinch/over-travel damages jig or injures operator | 2 | 3 | 6 | End-stops, current limit, E-stop, guards | Eng |
| R-07 | Component availability/import delays in Uzbekistan | 3 | 3 | 9 | Choose widely stocked parts; record real lead times from quotes | Owner |
| R-08 | Budget overrun from early expensive hardware | 3 | 3 | 9 | Approval gate; dev-kit first, custom PCB later | Owner |
| R-09 | Python reference and firmware DSP diverge | 3 | 3 | 9 | Shared test vectors; CI | Eng |
| R-10 | Unclear regulatory pathway delays any future product | 4 | 4 | 16 | Early research notes in `business/regulatory`; no claims of approval | Owner |
| R-11 | False activations (rest signal crosses threshold) | 4 | 3 | 12 | Hysteresis, minimum-duration, rest-data tests (SP-05) | Eng |
| R-12 | Dataset licensing / personal-data issues | 2 | 3 | 6 | Use only datasets with clear licence; record licence per dataset | Eng |
