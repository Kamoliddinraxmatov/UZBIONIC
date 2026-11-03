# UZBIONIC

**UZBIONIC — Inson imkoniyatlarini qayta kashf etuvchi texnologiya. O'zbekistonda ishlab chiqilgan, butun dunyo uchun yaratilgan.**

A non-invasive bionic hand controlled by surface EMG. Goal of the current plan: a first prototype a
person can wear, designed and built from scratch, bench-tested before anyone wears it
(see the safety gate in [docs/00-project-charter.md](docs/00-project-charter.md)).

## Repository layout

| Folder | Content |
|---|---|
| `docs/` | Charter, requirements, architecture, risks, roadmap, decisions (`adr/`), safety |
| `emg/` | EMG signal processing — Python reference pipeline and tests |
| `simulation/` | Synthetic EMG generator, kinematics, host-in-the-loop |
| `firmware/` | Microcontroller code (hardware-independent core + HAL) |
| `electronics/` | Schematics, PCB, BOM (candidates vs selected; real quotes only) |
| `mechanical/` | Our own CAD, exports (STL/STEP), drawings, calculations |
| `testing/` | Bench procedures, fixtures, dated reports |
| `business/` | Market, regulatory research (no claimed approvals), costing, partners |
| `tools/` | Helper scripts |

## Quick start (M0 — PC only)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
python tools/demo_pipeline.py          # writes demo_pipeline.png
```

## CAD (our own design)

```bash
pip install -r requirements-cad.txt
python mechanical/cad/export_finger.py   # one finger, placeholder sizes
python mechanical/cad/export_hand.py     # full hand + wrist rotator on standard sizes (docs/10-hand-cad.md)
```

## Rules

- No invented hardware specs, prices, clinical evidence or regulatory approvals. Unknown = `TBD`.
- No human-use testing before the safety gate is passed.
- Licence: open project with our own design; the exact licence is not chosen yet (decision D-14).
