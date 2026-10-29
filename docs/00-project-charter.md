# Project Charter — UZBIONIC (v0.2, 2026-10-29)

> UZBIONIC — Inson imkoniyatlarini qayta kashf etuvchi texnologiya. O'zbekistonda ishlab chiqilgan, butun dunyo uchun yaratilgan.

## 1. Purpose
Develop a non-invasive bionic hand controlled by surface electromyography (sEMG). The end goal of
the current plan (approved 2026-10-29) is a **first prototype a person can wear**, designed and built
from scratch. Everything is developed and verified on the bench first; first wearing happens only
after the safety gate in section 3a is passed.

## 2. Objectives (phase 1)
1. A documented, version-controlled engineering baseline (this foundation).
2. An offline EMG processing pipeline verified on synthetic and replayed data.
3. A bench prototype: EMG signal source → acquisition → controller → actuated finger(s),
   verified with instruments, not with a person.
4. Evidence-based requirements and a hardware selection backed by datasheets and real quotes.

## 3. Scope
**In scope:** mechanical design, electronics, firmware, EMG signal processing, simulation,
bench test procedures, business and regulatory *research* documentation.

**Out of scope (until the safety gate in 3a is passed):**
- Any human-use testing, including fitting the device to a person or wearing it.
- Invasive or implanted sensing of any kind.
- Clinical claims, efficacy claims, or statements of regulatory approval.
- Sales or distribution to users.

## 3a. Safety gate before first wearing
All of the following are required, and the owner approves the gate in writing:
- All bench tests passed and recorded.
- Battery-only operation while worn; never connected to a PC or charger; battery protection (BMS).
- Limited finger force; hand can be opened manually; no sharp edges.
- Skin-contact materials and socket reviewed by a prosthetist or doctor, who attends the session.
- Written informed consent from the wearer; written stop criteria (pain, skin redness, unexpected motion).
- No regulatory approval is claimed; this is a prototype trial, not a sale.

## 3b. Licence decision (D-14, 2026-10-29)
Open project, our own design: all mechanical/3D design is drawn from scratch by UZBIONIC; other
projects (Dextra, Open Bionics Ada, etc.) are used for ideas only. Design and code are published
openly under UZBIONIC authorship; the exact licence (CERN-OHL or CC BY-SA candidates) is still to
be chosen, so the repository has no LICENSE file yet. GPL code reused in firmware keeps its licence
and attribution. The UZBIONIC name and logo are a brand, protected separately.

## 4. Guiding principles
- **No invented data.** Hardware specs come from datasheets (cited), prices only from real,
  dated quotes, clinical/regulatory statements only from cited primary sources. Unknown = `TBD`.
- **Bench first.** Every function must first be verifiable on a bench with instruments, signal
  generators, recorded/synthetic data, and test fixtures.
- **Safety by design.** Current limiting, mechanical end-stops, emergency stop, fail-safe
  (relax/hold — decision D-07) on signal loss.
- **Small, testable steps.** Each milestone has written acceptance criteria.
- **Approval gates.** Substantial code and any expensive hardware purchase require the
  project owner's approval.

## 5. Stakeholders
| Role | Who | Responsibility |
|---|---|---|
| Project owner | Kamoliddin | Approves scope, gates, purchases |
| Engineering assistant | Claude | Drafts docs, code, analysis on request |
| Medical/ethics advisor | TBD | Needed before any human involvement |
| Prosthetist advisor | TBD | User needs, socket/interface knowledge |

## 6. Success criteria for phase 1
- M0–M3 of the roadmap accepted against their criteria.
- Zero undocumented hardware assumptions in the BOM.

## 7. Constraints
Budget: TBD (D-01). Schedule: TBD. Team size: TBD. Manufacturing access (3D printer type,
PCB fab): TBD (D-09).
