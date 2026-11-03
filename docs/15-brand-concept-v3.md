# Brand concept v3: "dark graphite" benchmark design (2026-10-30)

The owner made this concept render (`docs/concept/uzbionic-concept-v3.jpg`, made with an AI image tool)
and wrote a specification for it. The owner names it the project's **benchmark design**. It replaces the
white references as our visual target. It is our own brand concept, so we may follow it closely.

This document turns the owner's specification into requirements and flags where it conflicts with what
we already know. It **adds to** `01-requirements.md` and `02-system-architecture.md` and does not
replace them. Requirement IDs here use new prefixes (BRD, CMF) or continue existing ones.

The render is an image, not engineering data. Nothing in it is a measured size, a chosen part, a
material test or an approval.

## 1. What the concept shows
- **Closed version.** Modular graphite and slate armour panels; "UZBIONIC" with a small Uzbek flag on
  the forearm; a sun with "UZB" on the back of the hand; a tagline line on a panel; an elbow joint; a
  light, soft cuff at the top.
- **Open version.** The same arm with its panels off: carbon-look fingers with MCP, PIP and DIP joints;
  a multi-axis opposable thumb; tendon routing; an electronics block labelled "sEMG signal processing
  hub" on the forearm, with wiring to the actuators.

Note: the small text in the render is garbled (the image tool invents letters). Every printed word must
be set by us.

## 2. Requirements taken from the concept
| ID | Requirement | Source | Status |
|---|---|---|---|
| BRD-01 | The arm SHALL carry the UZBIONIC wordmark on the forearm. | Concept | Wordmark exists in CAD (radial side). Placement TBD. |
| BRD-02 | The back of the hand SHOULD carry the UZBIONIC sun emblem. | Concept | The emblem has to be drawn as clean vector art. |
| BRD-03 | A tagline SHOULD appear on one panel. English candidate: "Human ability. Engineered in Uzbekistan." The Uzbek slogan is in the charter. | Owner | Wording to be confirmed by the owner. |
| BRD-04 | Use of the national flag and of the emblem on a commercial product SHALL be checked against Uzbek rules before release. | Our addition | Open: needs a lawyer, together with the trademark (charter 3b). |
| CMF-01 | Main colours: dark graphite and slate grey panels, matte and semi-gloss finishes. Accents: carbon-look fingers and frame. | Concept | Replaces the white palette of look v0.2. |
| CMF-02 | Panel material candidates: PA12 (usually SLS, made by a print service) or carbon-fibre nylon (FDM, needs a hardened nozzle and an enclosure). PETG or PLA for bench prototypes. | Owner (as assumptions) | **Candidates only.** To choose after print and strength tests. |
| MEC-06 | The outer panels SHOULD come off without damaging them, for maintenance. The open-version view is the same arm with its panels removed. | Concept | Panel split and clips not designed yet (see doc 12). |
| MEC-07 | Five fingers with MCP, PIP and DIP joints, tendon-driven, and an opposable thumb. | Concept | **Already built:** CAD v0.2, 5 × Pololu #5201. Thumb rotation is passive with detents in v1. |
| MEC-08 | Wrist and elbow SHOULD be modules that can be swapped. | Concept | Wrist rotator exists (bolt pattern). Elbow is a later phase (passive lockable in v1). |
| ELE-04 | An electronics bay in the forearm holds the sEMG analog front end, the MCU and the motor drivers, wired to the hand through the wrist. | Concept | Fits the architecture. Bay volume not yet reserved in CAD. |
| SAF-07 | Grip force SHALL be limited in firmware and by motor current, with the limit set from bench tests. | Owner | Same as SAF-03. The value is still TBD. |

## 3. Where the concept does not fit our first user, and what we do instead
| Concept shows | Fact | Our decision |
|---|---|---|
| sEMG sensor array on the back of the forearm | The first user is a **transhumeral** amputee (left arm, above the elbow). There are no forearm muscles. | sEMG electrodes go on the residual **upper arm** (biceps and triceps) inside the socket. The forearm only holds the processing bay. |
| Light soft cuff at the top, called a "muscle interface" | The socket carries the whole arm's weight and must be fitted to the person. | The socket is made **with a prosthetist**. We design only its standard interface to our elbow. No fitting on a person until the safety gate (SAF-01). |
| Gesture classification | Our v1 uses 2 sensors: biceps closes, triceps opens, co-contraction switches mode (PR #2). | Pattern-recognition gestures come in v2, with 6–8 channels. |
| Carbon-fibre fingers | Our printers do PLA and PETG. Carbon nylon needs special hardware. | Print in PLA or PETG first. Carbon-look is a finish or a later material. |
| SolidWorks / Fusion 360 | Our CAD is CadQuery (code, tested). | We keep CadQuery as the source. STEP export opens in Fusion or SolidWorks for a designer. |

## 4. Next steps
1. CAD look v0.3: graphite palette, armour-style panel lines and the emblem. The existing tested
   geometry is reused.
2. Reserve the electronics bay in the forearm (ELE-04), and design how the panels split and clip on
   (MEC-06).
3. BOM: the existing purchase list, plus the MCU, battery, sEMG front end and drivers (prices only from
   real quotes).
4. Firmware: grip-force limit (SAF-07) on top of the PR #2 control code.
