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

## Cover mounting (2026-10-30)
The owner's visual design is the outer cover. The skeleton stays hidden inside it. Each cover piece is
printed separately and screwed to its own phalanx, so it moves with that phalanx.

Each phalanx has **two blind pilot holes** on its back: Ø1.6 mm, 4.5 mm deep, for M2 self-tapping
screws. They sit off the centre line (±0.28 × width), so they miss the return tendon, and diagonally on
the straight body, clear of the tongue and the fork slot. `finger.mount_points(params, index)` gives
their positions in the phalanx frame. A cover designed around the skeleton puts its screw bosses at
those points. Covers keep about 1 mm of free gap at each joint. Clearances for covers are checked as in
`docs/12-outer-shell.md`.
