# Finger drive v0.1: motors and spools in the palm (2026-10-30)

Decision D-04 (owner, 2026-10-30): **5 × Pololu 380:1 Micro Metal Gearmotor HPCB 6V with 12 CPR encoder,
side connector (Pololu #5201)**, one per finger including the thumb. Cable: Pololu #4763 (6-pin JST SH,
single-ended, 30 cm), one per motor plus a spare. Not ordered yet. The owner is checking shipping.

Source: `mechanical/cad/drive.py`. Tests: `mechanical/tests/test_drive.py`. Picture:
`mechanical/exports/hand/drive_preview.png`. Printable parts: `motor_carrier`, `spool_*`.

## Motor data used (Pololu product page and dimension drawing)
| Item | Value |
|---|---|
| Gearbox cross section | 10 × 12 mm |
| Length without shaft, encoder versions | up to 32.5 mm (plain HPCB 25.6 mm) |
| Output shaft | 9 mm long, Ø3 mm D-shaft |
| No-load speed / current at 6 V | 85 rpm / 150 mA |
| Stall (extrapolated, theoretical) | 5.0 kg·cm, 1.5 A |
| Recommended instantaneous torque limit, 380:1 gearbox | 2.5 kg·cm |
| Price | 29.85 USD each at 5+ (pololu.com, 2026-10-30) |

The encoder end with the side connector is modelled as 14 mm across. That is read off the drawing, so
check it on the real motor.

## Layout (design)
- The motors lie across the palm (axis along Y) in five rows, rear to front: thumb, little, ring,
  middle, index. Row pitch is 13.2 mm. That fills the cavity, so there is **no room for a 6th motor in
  the palm**.
- Each spool sits directly behind its finger's knuckle, so the flexor tendon runs straight back, under
  the other motors, and winds onto the bottom of its spool. Spool core is R5.5 mm, flanges R6.5 mm.
- A carrier plate under the cover has one rib per motor (gearbox face against the rib, shaft through
  it). Encoder connectors point up through slots in the plate.
- The cover's locating lips now run only along the two long sides, so the front and back rows fit.

## Estimates (to be measured on the bench)
- At the gearbox limit of 2.5 kg·cm, tendon pull = 0.245 N·m / 5.5 mm ≈ **45 N** per finger.
- Fingertip and grip force depend on the contact point and the joint moment arms (≈5 mm). Power grip
  in the low tens of newtons per finger is plausible but **not verified**. Measure it with a force
  gauge on the bench.
- Firmware must limit current (stall is 1.5 A and can damage the gearbox) and stop on the encoder end
  position.

## Checked by tests
- Motors, spools and carrier do not collide with each other, the palm or the cover.
- Each finger's straight tendon path from the knuckle to its spool clears every other motor and spool.
- Spools are aligned with their fingers. Tendon pull at the gearbox limit is in the 40–50 N band.

## Open
- Thumb tendon route: through the hollow thumb axle, then a guide turns it into the thumb spool (not
  modelled).
- Motor fixing: M1.6 screws through the rib into the gearbox face plate. Hole positions must be taken
  from the drawing or the motor itself.
- Elastic return cords, wiring path to the wrist, motor drivers and current sensing (electronics phase).
