# Forearm shell v0.1: brand form study, wrist to elbow (2026-10-30)

Owner's decision (2026-10-30): build the brand model first, as **our own design in the style of the
reference images**, not a copy. The references were concept art by another artist ("NEO CULTURE
TECHNOLOGY" label), so they gave ideas only: glossy white shell, perforated soft panel, grey grip panel
with contour lines, graphite wrist ring, visible elbow hub. Shapes, panel outlines and wordmark are ours.

Source: `mechanical/cad/forearm.py`. Tests: `mechanical/tests/test_forearm.py` (about 9 min).
Exports: `mechanical/exports/forearm/` (STL + STEP + renders). Renders: `python tools/render_hand.py
mechanical/exports/forearm arm`.

## Parts
| Part | What |
|---|---|
| `forearm_shell` | White elliptical shell, 2 mm wall, open at both ends. UZBIONIC is engraved on the radial side near the elbow. |
| `forearm_mesh` | Perforated lens-shaped panel on the back, recessed 0.8 mm, with Ø1.2 holes at 3.6 mm pitch. |
| `forearm_grip` | Grey oval pad on the ulnar side with 4 contour grooves. |
| `elbow_hub` | Elbow housing **envelope only**. The elbow mechanism (passive lockable for v1) is a later phase. |
| `forearm_cuff` | White cuff fixed to the palm shell. It turns with the hand and blends the round wrist into the flat palm. |

## Sizes
**Placeholders.** Length 250 mm (wrist joint to elbow axis) and the section widths are design values,
labelled in `ForearmParams.stations`. They are to be replaced by the first user's measured right
forearm, mirrored: length elbow to wrist, wrist circumference and largest circumference. Only the
wrist end is fixed by our parts: it must slide over the wrist stator (Ø56), and the parameters reject
a smaller wrist end.

## Checked by tests
- All parts are valid solids and do not collide with each other.
- The parts clear the wrist stator, the rotor and the whole dressed hand at wrist angles −90°, 0° and
  +90°. The cuff turns with the hand.

## Honest limits / next
- The form is a smooth tube with panels. It reads as a product, but it is not yet as sculpted as the
  references.
- The hand is the weak part: its palm is flat and boxy next to the round wrist. Next is v0.2 of the
  hand: a tapered palm, a thenar bulge and tapered fingers.
- The wrist is round, Ø56, because of the placeholder rotator. A real wrist is flatter (wider than
  thick). Once the wrist motor is chosen, the rotator should shrink.
- Not designed yet:
  - how the shell splits for printing (two halves plus clips);
  - the inner frame, and space for the battery and electronics;
  - the socket and elbow (with a prosthetist).
