# Look v0.2: brand model close to the owner's references (2026-10-30)

The owner asked for the exact look of a set of concept-art images by another artist. A one-to-one copy
would infringe that artist's copyright, and it contradicts decision D-14 (open, but the design is
ours). So v0.2 takes the references' **visual language** and draws every shape ourselves.

Source: `mechanical/cad/style_v2.py`. Tests: `mechanical/tests/test_style_v2.py` (about 3.5 min).
Renders: `mechanical/exports/style_v2/`, made with `python tools/render_hand.py
mechanical/exports/style_v2 v2`.

| Element of the look | How v0.2 does it |
|---|---|
| Metal fingers with white pads | The phalanges are shown as bright metal. White pads on their back and palm side are cut from the v0.1 covers, so they keep the covers' clearances. Fingertips stay white and rounded. |
| Perforated white surfaces | Perforated back of the hand and forearm sleeve. **The holes are a render pattern only.** Whether printed parts get real holes waits for print tests. |
| Hard white frame | Thumb-side strip of the palm shell. On the forearm, the little-finger side, which wraps diagonally over the back towards the elbow. |
| Open window showing the inside | A large lens-shaped window in the forearm sleeve shows a dark inner liner (textile or a printed lattice). |
| Grey "contour line" pads | Terraced pads on the thenar and hypothenar areas, on the forearm's hard side, and a ribbed bar under the knuckles. |

Checked: the new parts are valid and clear the skeleton, the motors, the wrist and each other, with
the thumb at both 0° and 108°.

Still different from the references: their shapes are sculpted freely (sub-D modelling). Ours are
parametric lofts and boxes, so the palm is still boxy. Getting that sculpted feel needs a sculpting
pass, by us in Blender or by a designer, over these parts.
