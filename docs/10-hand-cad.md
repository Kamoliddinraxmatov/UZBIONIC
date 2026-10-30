# Hand CAD v0.2: palm, thumb, wrist rotator on standard sizes (2026-10-30)

Owner's instruction (2026-10-30): build everything to standard sizes and learn from competitors, rather
than wait for measurements. Our own design (decision D-14): competitors gave us ideas only. No geometry
was copied.

Source: `mechanical/anthropometry.py` (sizes), `mechanical/hand_layout.py` (layout + kinematics, no CAD
needed), `mechanical/cad/hand.py` (palm, cover, thumb), `mechanical/cad/wrist.py` (wrist rotator).
Exports: `mechanical/exports/hand/` (19 parts as STL + STEP, `hand_preview.png`). Regenerate with
`python mechanical/cad/export_hand.py` after `pip install -r requirements-cad.txt`.

## 1. Where the sizes come from
| What | Value | Source |
|---|---|---|
| Hand length × breadth | 190 × 85 mm (default) | Inside the 180–198 × 75–90 mm range a prosthetic hand should match (Belter et al. 2013, J. Rehabil. Res. Dev. 50(5)) |
| Phalanx lengths | % of hand length, e.g. index 21.8 / 14.1 / 8.6 | Freivalds (32 subjects), as tabulated in "A Functional Anatomy Based Kinematic Human Hand Model with Simple Size Adaptation" (DLR), Table II |
| Fingertip pad | +4 mm on the distal segment | Design value (the source lengths stop at bone/joint) |
| Finger width / height, palm thickness 28 mm, MCP setback, thumb layout | see code | **Design values**, marked "design" in code |

Every size scales from `HandSize(hand_length, hand_breadth)`. Once the first user's right hand is
measured, set those two numbers (and any measured segment) and re-export. Mirroring for the left hand
is already built in (`side="left"`, the default).

## 2. What we learned from competitors (ideas only)
| Idea | Seen in | How we use it |
|---|---|---|
| Target mass under ~500 g, power grip ≥ 45 N (68 N enough for daily living), closing ≈ 1 s | Belter et al. 2013 review of i-Limb, bebionic, Michelangelo, Vincent | Design targets for the motor choice (D-04) |
| 6 DOF hands typically use 5–6 motors, one flexion motor per finger | bebionic, i-Limb (5 motors), Ability Hand (6 motors incl. thumb rotation) | 5 flexion motors in the palm. Thumb rotation is positioned by hand in v1 (detents), so we keep 6 motors in total with the wrist |
| Thumb base turns between lateral (key grip) and opposed (pinch, tripod, power) | bebionic, i-Limb | Thumb hub on an axle along the palm, 0° lateral / 108° opposed, spring-pin detents |
| Powered wrist rotation; Hero Arm advertises 180° | Open Bionics Hero Arm | Coaxial wrist rotator with ±90° travel and a hard stop |
| Hollow palm with motors inside, removable cover | bebionic, Hero Arm | Palm cavity ≈ 67 × 80 × 25 mm with a back cover |
| Fingertip pressure sensors | Ability Hand, concept images | **v2.** v1 detects a grip from motor current |
| Style: white shell, perforated soft panels, dark fingers, hex rubber grip pads, grey wrist ring | Owner's Pinterest references (mostly concept art) | For the outer shell, drawn after the mechanics work |

Competitor numbers (Belter et al. 2013, Table 1/2): bebionic v2 495–539 g, power grip 75 N, 5 motors;
i-Limb 450–615 g, 5 motors. Ability Hand (public spec compilation): 490 g, 6 motors, 66 N power grip.

## 3. Design
- **Palm**: hollow box with rounded corners, open at the back, plus a cover. Four knuckle forks take
  the fingers' proximal tongues; they use the same fork and extension stop as the finger joints
  (`finger.fork_block`). Each fork has flexor and return tendon holes into the cavity.
- **Thumb**: the metacarpal is a hub on a hollow 4 mm axle along the palm's thumb edge. The arm carries
  the fork for the thumb's two phalanges. The palm has clearance for the arm's whole travel (the arm's
  swept volume is cut out). Two detent holes, at 0° and 108°, take a spring pin through the hub.
  The thumb flexor tendon runs through the hollow axle, so turning the thumb barely changes its length.
- **Wrist rotator**: the stator cup holds the motor (coaxial) and a bearing. The rotor sits in the
  bearing, takes the motor shaft and carries the palm on 3 × M3 screws (Ø36 mm circle). A tab on the
  rotor runs in a groove in the stator and hits a stop block, giving ±90° of travel and never more.
  Cables go beside the motor, then through an arc slot in the rotor into the palm's 26 mm cable hole.

## 4. Checked by tests
`mechanical/tests/test_layout.py`, `test_hand.py`, `test_wrist.py` (71 tests in the whole repo pass):
- The default size is inside the Belter range. Segments scale with hand length. Left is the exact
  mirror of right. The thumb is on the index side.
- **Pinch**: with the thumb opposed, its tip reaches within 5 mm of the index tip, in front of the
  palm and on the palm side (best 2.1 mm). Tripod: within 12 mm of the middle tip. In the lateral
  position the thumb cannot pinch.
- 5° short of the best pinch pose, the pads are < 10 mm apart and no parts collide, so a thin
  object would be held there.
- The open hand has no collisions between any of its 16 parts. The thumb turns through its whole
  0–108° travel without touching the palm. Fingers cannot bend backwards at the knuckle (the palm stops
  them). The detent holes line up with the hub pin at both positions.
- Wrist: free at −90…+90°, blocked at ±95° and 180°. The palm bolt pattern and cable hole match the
  rotor. Inconsistent stop or too-short stator parameters are rejected.

## 5. Mass estimate (plastic only)
Solid volume × typical PLA density (≈1.24 g/cm³), so this is an upper bound for the printed parts:
hand ≈ 208 g (palm 62, cover 20, thumb 32, fingers 94), wrist ≈ 125 g. Motors, gearboxes,
electronics, battery and shell are **not** included. The total must be measured once parts are
chosen. For a transhumeral user, weight is a top risk.

## 6. Not decided / not verified
- **Motors (D-04)**: the palm cavity and the wrist's motor envelope (Ø24 × 30 mm) are placeholders.
  The bearing (42/30/7 mm, a thin-section 6806-class size) must be confirmed against the part bought.
- Tendon spools, motor mounts inside the palm, wiring and the cover screws: next CAD step, after D-04.
- Strength, friction, print fit and grip force: not verified until a test print on the bench.
- The thumb layout was tuned by a kinematic search (pinch and tripod distance). It will need re-tuning
  for the measured hand.
- Forearm, elbow (passive lockable for v1), socket (with a prosthetist): later phases.
- No human-use testing (charter, safety gate).
