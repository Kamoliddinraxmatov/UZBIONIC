"""Photo-style previews of the dressed hand (skeleton + outer shell), rendered with three.js.

Usage: python tools/render_hand.py [output_dir] [view-name prefix]   (default mechanical/exports/shell, all views)
Needs: requirements-cad.txt, Node.js with Playwright's Chromium, and `npm install` in tools/render.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mechanical.anthropometry import FINGERS  # noqa: E402
from mechanical.cad.forearm import ForearmParams, _loft, _x_back, forearm_parts  # noqa: E402
from mechanical.cad.hand import Grip, PalmParams  # noqa: E402
from mechanical.cad.shell import dressed  # noqa: E402
from mechanical.cad.style_v2 import dressed_v2, forearm_v2, material_v2  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402
from mechanical.hand_layout import best_pinch  # noqa: E402

HIDDEN = ("palm",)  # inside the shell, not visible


def material(name: str) -> str:
    if name.startswith("shell_"):
        return "shell"
    if name.startswith(("pad_", "forearm_grip")):
        return "pad"
    if name in ("forearm_shell", "forearm_cuff"):
        return "shell"
    if name == "forearm_mesh":
        return "mesh"
    if name == "forearm_liner":
        return "inner"
    if name.startswith("wrist"):
        return "ring"
    return "joint"


def views(pp: PalmParams) -> dict:
    L = pp.layout
    _, thumb, index, _ = best_pinch(L, "index", step=5)
    pinch_fingers = {f: (35.0, 45.0, 30.0) for f in FINGERS}
    pinch_fingers["index"] = index
    pinch = Grip(thumb_rotation=L.thumb_opposed_deg, thumb=(thumb[0] - 5, thumb[1] - 5), fingers=pinch_fingers)
    m = L.mirror
    # relaxed hand: fingers slightly curled, more towards the little finger, thumb half turned
    relaxed = Grip(
        thumb_rotation=35.0,
        thumb=(10.0, 10.0),
        fingers={"index": (8.0, 12.0, 8.0), "middle": (10.0, 15.0, 10.0), "ring": (13.0, 18.0, 12.0), "little": (16.0, 22.0, 14.0)},
    )
    # name: (grip, camera direction, up, with forearm)
    return {
        "hand_open_back": (relaxed, (-0.35, 0.55 * m, 1.0), (1, 0, 0), False),
        "hand_open_palm": (relaxed, (-0.3, 0.45 * m, -1.0), (1, 0, 0), False),
        "hand_pinch": (pinch, (0.25, 1.0 * -m, -0.55), (0, 0, 1), False),
        # arm hanging, fingers down, like a product shot
        "arm_back": (relaxed, (0.15, 0.45 * m, 1.0), (-1, 0, 0), True),
        "arm_radial": (relaxed, (0.1, 1.0 * m, 0.4), (-1, 0, 0), True),
        "arm_ulnar": (relaxed, (0.1, -1.0 * m, 0.4), (-1, 0, 0), True),
        # v0.2 look (style_v2), same cameras
        "v2_arm_back": (relaxed, (0.15, 0.45 * m, 1.0), (-1, 0, 0), "v2"),
        "v2_arm_radial": (relaxed, (0.25, 1.0 * m, 0.55), (-1, 0, 0), "v2"),
        "v2_arm_ulnar": (relaxed, (0.1, -1.0 * m, 0.4), (-1, 0, 0), "v2"),
        "v2_hand_palm": (relaxed, (-0.3, 0.45 * m, -1.0), (1, 0, 0), "v2hand"),
    }


def forearm_scene() -> dict:
    """Forearm shell parts, plus a dark liner inside it so the perforations read as holes (render only)."""
    fp = ForearmParams()
    parts = forearm_parts(fp)
    parts["forearm_liner"] = _loft(fp, -fp.wall - 3.0, fp.start_x - 2, _x_back(fp) + 2)
    return parts


def mesh(part, tol=0.15):
    verts, tris = part.val().tessellate(tol, 0.2)
    return [c for v in verts for c in (v.x, v.y, v.z)], [i for t in tris for i in t]


def main(out_dir: str = "mechanical/exports/shell", only: str = "") -> None:
    pp = PalmParams()
    out = ROOT / out_dir
    out.mkdir(parents=True, exist_ok=True)
    wp = WristParams()
    with tempfile.TemporaryDirectory() as tmp:
        scene_files = []
        arm = arm2 = None
        for name, (grip, view, up, with_arm) in views(pp).items():
            if only and not name.startswith(only):
                continue
            v2 = isinstance(with_arm, str)
            pick = material_v2 if v2 else material
            parts = dressed_v2(pp, grip) if v2 else dressed(pp, grip)
            if with_arm is True:
                arm = arm or forearm_scene()
                parts.update(arm)
            elif with_arm == "v2":
                arm2 = arm2 or forearm_v2()
                parts.update(arm2)
            parts["wrist_rotor"] = rotor(wp)
            parts["wrist_stator"] = stator(wp)
            items = []
            for pname, part in parts.items():
                if pname in HIDDEN:
                    continue
                pos, idx = mesh(part)
                items.append({"name": pname, "material": pick(pname), "positions": pos, "indices": idx})
            path = Path(tmp) / f"{name}.json"
            with_arm = with_arm in (True, "v2")
            size = (1000, 1400) if with_arm else (1200, 1200)
            spec = {"width": size[0], "height": size[1], "view": view, "up": up, "parts": items}
            if with_arm:
                spec["zoom"] = 1.0
            path.write_text(json.dumps(spec))
            scene_files.append(str(path))
        subprocess.run(["node", str(ROOT / "tools/render/render.mjs"), str(out), *scene_files], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
