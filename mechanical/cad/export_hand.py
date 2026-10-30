"""Export the hand (palm, cover, thumb, all phalanges) and the wrist rotator as STL + STEP, with preview images.

Usage: python mechanical/cad/export_hand.py [output_dir]   (default mechanical/exports/hand)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import cadquery as cq  # noqa: E402

from mechanical.anthropometry import FINGERS  # noqa: E402
from mechanical.cad.finger import finger  # noqa: E402
from mechanical.cad.hand import Grip, PalmParams, assembled, palm, palm_cover, thumb_metacarpal  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402

GRIPS = {
    "open": Grip(),
    "power": Grip(thumb_rotation=108, thumb=(15, 10), fingers={f: (55, 65, 43) for f in FINGERS}),
    "pinch": Grip(thumb_rotation=108, thumb=(25, 20), fingers={"index": (10, 90, 60), "middle": (60, 80, 53), "ring": (60, 80, 53), "little": (60, 80, 53)}),
}


def scene(pp: PalmParams, grip: Grip, wrist_angle: float = 0.0) -> dict:
    parts = assembled(pp, grip)
    wp = WristParams()
    parts["wrist_rotor"] = rotor(wp, wrist_angle)
    parts["wrist_stator"] = stator(wp)
    return parts


def render_preview(path: Path, pp: PalmParams) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = LightSource(azdeg=225, altdeg=45)
    fig = plt.figure(figsize=(18, 7))
    for k, (name, grip) in enumerate(GRIPS.items()):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d")
        for pname, part in scene(pp, grip).items():
            color = "#e9edf1" if pname.startswith(("palm", "wrist")) else ("#5b6670" if "thumb" not in pname else "#7d8892")
            if pname == "thumb_metacarpal":
                color = "#e9edf1"
            verts, tris = part.val().tessellate(0.3)
            pts = [[(v.x, v.y, v.z) for v in (verts[a], verts[b], verts[c])] for a, b, c in tris]
            ax.add_collection3d(Poly3DCollection(pts, facecolors=color, shade=True, lightsource=light))
        ax.set_xlim(-50, 170)
        ax.set_ylim(-150, 70)
        ax.set_zlim(-140, 80)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=30 if name == "open" else -20, azim=-60 if name == "open" else -40)
        ax.set_axis_off()
        ax.set_title(name)
    fig.suptitle("UZBIONIC hand v0.2 (left) — standard sizes, hand length 190 mm; motors and shell not drawn yet")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.9, wspace=0)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def main(out_dir: str = "mechanical/exports/hand") -> None:
    pp = PalmParams()
    out = ROOT / out_dir
    out.mkdir(parents=True, exist_ok=True)
    parts = {"palm": palm(pp), "palm_cover": palm_cover(pp), "thumb_metacarpal": thumb_metacarpal(pp)}
    for f in FINGERS + ("thumb",):
        fp = pp.thumb_params() if f == "thumb" else pp.finger_params(f)
        for name, part in zip(fp.names, finger(fp)):
            parts[f"{f}_{name}"] = part
    wp = WristParams()
    parts["wrist_stator"] = stator(wp)
    parts["wrist_rotor"] = rotor(wp)
    for name, part in parts.items():
        cq.exporters.export(part, str(out / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(part, str(out / f"{name}.step"))
    render_preview(out / "hand_preview.png", pp)
    print(f"wrote {len(parts)} parts to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
