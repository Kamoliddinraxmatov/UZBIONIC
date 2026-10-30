"""Photo-style previews of the dressed hand (skeleton + outer shell), rendered with three.js.

Usage: python tools/render_hand.py [output_dir]   (default mechanical/exports/shell)
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
from mechanical.cad.hand import Grip, PalmParams  # noqa: E402
from mechanical.cad.shell import dressed  # noqa: E402
from mechanical.cad.wrist import WristParams, rotor, stator  # noqa: E402
from mechanical.hand_layout import best_pinch  # noqa: E402

HIDDEN = ("palm",)  # inside the shell, not visible


def material(name: str) -> str:
    if name.startswith("shell_"):
        return "shell"
    if name.startswith("pad_"):
        return "pad"
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
    return {
        "hand_open_back": (relaxed, (-0.35, 0.55 * m, 1.0), (1, 0, 0)),
        "hand_open_palm": (relaxed, (-0.3, 0.45 * m, -1.0), (1, 0, 0)),
        "hand_pinch": (pinch, (0.25, 1.0 * -m, -0.55), (0, 0, 1)),
    }


def mesh(part, tol=0.15):
    verts, tris = part.val().tessellate(tol, 0.2)
    return [c for v in verts for c in (v.x, v.y, v.z)], [i for t in tris for i in t]


def main(out_dir: str = "mechanical/exports/shell") -> None:
    pp = PalmParams()
    out = ROOT / out_dir
    out.mkdir(parents=True, exist_ok=True)
    wp = WristParams()
    with tempfile.TemporaryDirectory() as tmp:
        scene_files = []
        for name, (grip, view, up) in views(pp).items():
            parts = dressed(pp, grip)
            parts["wrist_rotor"] = rotor(wp)
            parts["wrist_stator"] = stator(wp)
            items = []
            for pname, part in parts.items():
                if pname in HIDDEN:
                    continue
                pos, idx = mesh(part)
                items.append({"name": pname, "material": material(pname), "positions": pos, "indices": idx})
            path = Path(tmp) / f"{name}.json"
            path.write_text(json.dumps({"width": 1200, "height": 1200, "view": view, "up": up, "parts": items}))
            scene_files.append(str(path))
        subprocess.run(["node", str(ROOT / "tools/render/render.mjs"), str(out), *scene_files], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
