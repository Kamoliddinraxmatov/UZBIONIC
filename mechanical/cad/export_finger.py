"""Export the finger phalanges as STL (for printing) and STEP (for other CAD tools), plus a preview image.

Usage: python mechanical/cad/export_finger.py [output_dir]   (default mechanical/exports/finger)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import cadquery as cq  # noqa: E402

from mechanical.cad.finger import FingerParams, assembled, finger  # noqa: E402


def render_preview(path: Path, p: FingerParams) -> None:
    """Side view of the finger straight and curled, drawn from the tessellated solids."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = LightSource(azdeg=225, altdeg=45)
    fig = plt.figure(figsize=(12, 5.5))
    for k, (angles, title) in enumerate((((0, 0, 0), "straight"), ((0, 45, 60), "curled (45°, 60°)"))):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        colors = ("#c9d6e3", "#9fb7cf", "#6f93b8")
        for part, color in zip(assembled(p, angles), colors):
            verts, tris = part.val().tessellate(0.2)
            pts = [[(v.x, v.y, v.z) for v in (verts[a], verts[b], verts[c])] for a, b, c in tris]
            ax.add_collection3d(
                Poly3DCollection(pts, facecolors=color, shade=True, lightsource=light)
            )
        ax.set_xlim(-15, 95)
        ax.set_ylim(-55, 55)
        ax.set_zlim(-75, 35)
        ax.set_box_aspect((110, 110, 110))
        ax.view_init(elev=15, azim=-70)
        ax.set_title(title)
        ax.set_xlabel("X mm")
        ax.set_ylabel("Y mm")
        ax.set_zlabel("Z mm")
    fig.suptitle("UZBIONIC finger v0.1 — placeholder sizes, not measured")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main(out_dir: str = "mechanical/exports/finger") -> None:
    p = FingerParams()
    out = ROOT / out_dir
    out.mkdir(parents=True, exist_ok=True)
    for name, part in zip(p.names, finger(p)):
        cq.exporters.export(part, str(out / f"finger_{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(part, str(out / f"finger_{name}.step"))
    render_preview(out / "finger_preview.png", p)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
