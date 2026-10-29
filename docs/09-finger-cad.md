# Finger CAD v0.1 — our own parametric design (2026-10-29)

Source: `mechanical/cad/finger.py` (CadQuery). Exports: `mechanical/exports/finger/` (STL for
printing, STEP for other CAD tools, preview PNG). Regenerate with
`python mechanical/cad/export_finger.py` after `pip install -r requirements-cad.txt`.

Drawn from scratch for UZBIONIC (decision D-14); other open projects were used only for ideas.

## Design
- Three phalanges, pin hinges. Each joint: tongue on the child turning in a fork on the parent.
- Flexor tendon channel on the palm side below the pin axes (pull → finger curls); return channel on
  the back for an elastic cord (finger opens when the tendon is released).
- Extension stop: a lip behind each pin rests on a bridge in the fork, so joints curl towards the palm
  but cannot bend backwards past straight.
- The proximal phalanx has a tongue for the palm fork (palm not designed yet).
- Printing: lying on its side (Y up), so the pin holes print as round holes and the layers run along the
  finger. 0.3 mm clearance between moving parts (tunable).

## Checked by tests (`mechanical/tests/test_finger.py`)
- Valid solids.
- No collision between neighbouring phalanges at 0°, 30°, 60°, 90° and mixed angles.
- Bending backwards by 5° collides (the extension stop works).
- Pin holes are clear; too-short phalanges are rejected.

## Not yet decided / not verified
- **All sizes are placeholders, not measurements.** Lengths 42 / 26 / 22 mm, width 17 mm, height 15 mm
  must be replaced with the user's right-hand measurements, mirrored for the left hand.
- Pin material (2 mm steel pin or filament), tendon line and elastic cord: open, part of the BOM.
- Strength, friction and print fit are not verified until a test print.
- Thumb (different joints and rotation), palm, wrist rotator and socket: next steps.
