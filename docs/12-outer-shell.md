# Outer shell v0.1 (2026-10-30)

The owner pointed out that the mechanism alone does not look like a hand. This adds the outer shell. It is
our own design (D-14); the owner's reference images gave the style only.

Source: `mechanical/cad/shell.py`. Renders: `mechanical/exports/shell/*.png`, made by
`python tools/render_hand.py` (three.js in headless Chromium; run `npm install` in `tools/render` first).
Tests: `mechanical/tests/test_shell.py`.

## Design
- **Finger covers.** Each phalanx gets a rounded sleeve (wall 1.2 mm, 0.3 mm gap). The distal sleeve
  ends in a rounded fingertip with a grey grip pad.
- **Joint caps.** Each sleeve ends in a round cap around the next pin. The next sleeve starts outside
  that cap's circle, so neighbouring covers never touch whatever the joint angle. Seen from the back, the
  joint looks closed. The cap is cut where the next phalanx's body and its extension-stop lip pass. That
  cut leaves a small window behind each joint on the back.
- **Knuckle caps** cover the palm's knuckle forks in the same way.
- **Palm shell.** A rounded white shell around the palm and its cover, open at the knuckles, the wrist
  and the thumb's whole travel, with UZBIONIC engraved on the back. Grey grip pads sit on the palm side:
  a large palm pad and a bar under the knuckles.
- **Thumb.** A sleeve over the metacarpal arm with a cap at the thumb MCP. The palm's thumb clearance now
  includes room for this sleeve (`PalmParams.thumb_cover_allowance`).

## Checked by tests
- Every shell part is a valid solid.
- No collisions anywhere in the open hand, skeleton plus shell (42 parts).
- With the covers on, fingers bend freely at (30,30,30), (60,70,50) and (90,90,0) degrees.
- The thumb cover clears the palm and the palm shell at 0°, 54° and 108°.

## Honest limits / next
- The look is still "robotic": the palm is a rounded box and the fingers are uniform. v0.2 should taper
  the palm towards the wrist, add a thenar bulge at the thumb base and taper the fingers.
- A fully organic look like the reference concept art is normally sculpted by an industrial designer
  (Blender / Fusion 360 Form) around the skeleton's STEP files. Our parametric skeleton stays the
  source of truth for the fit.
- How each cover is split and clipped on for printing, TPU vs PLA, and the cover-to-palm fixing are
  not designed yet.
