"""Bring an AI-made visual 3D model of the arm (GLB/OBJ/STL) onto our skeleton: step 3 of the plan
"konseptdan chop etiladigan protezgacha" (2026-10-30).

What it does:
1. loads the file and merges it into one mesh, and reports its size and whether it is closed (watertight);
2. turns it so its long axis is our X axis (forearm to fingertips), scales it so it is as long as our
   arm (elbow axis to the middle fingertip) and moves it so the elbow end sits at the elbow;
3. checks how much of each skeleton part sticks out of it: the shell must enclose the skeleton.

Which end is the hand, and which side is the back of the hand, cannot be told reliably from the shape,
so check the report's preview and use --flip / --roll if needed.

Usage: python tools/import_shell.py model.glb [--out DIR] [--flip] [--roll DEG]
Output: DIR/shell_aligned.stl and DIR/report.json (default DIR mechanical/exports/import).
Units: mm.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_mesh(path: str) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene")
    meshes = [g for g in loaded.dump() if isinstance(g, trimesh.Trimesh)] if isinstance(loaded, trimesh.Scene) else [loaded]
    if not meshes:
        raise ValueError(f"no triangle mesh in {path}")
    return trimesh.util.concatenate(meshes)


def principal_frame(mesh: trimesh.Trimesh) -> np.ndarray:
    """Rotation (3x3, rows = new X, Y, Z) putting the longest extent on X, the next on Y."""
    pts = mesh.vertices - mesh.vertices.mean(axis=0)
    _, _, vt = np.linalg.svd(pts[:: max(1, len(pts) // 20000)], full_matrices=False)
    r = vt.copy()
    if np.linalg.det(r) < 0:
        r[2] *= -1
    return r


def target_length() -> tuple[float, float]:
    """(x of the elbow axis, x of the middle fingertip) of our skeleton."""
    from mechanical.cad.forearm import ForearmParams
    from mechanical.cad.hand import PalmParams
    from mechanical.cad.shell import GAP, WALL

    pp = PalmParams()
    fp = pp.finger_params("middle")
    tip = float(pp.layout.mcp("middle")[0]) + sum(fp.lengths) + GAP + WALL
    return -ForearmParams().length, tip


def align(mesh: trimesh.Trimesh, flip: bool = False, roll_deg: float = 0.0) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_translation(-m.vertices.mean(axis=0))
    t = np.eye(4)
    t[:3, :3] = principal_frame(m)
    m.apply_transform(t)
    # the hand end is usually the wider one (fingers spread): put it at +X unless told otherwise
    x = m.vertices[:, 0]
    lo, hi = np.percentile(x, 5), np.percentile(x, 95)
    width = lambda sel: np.ptp(m.vertices[sel, 1]) if sel.any() else 0.0  # noqa: E731
    hand_at_minus = width(x < lo) > width(x > hi)
    if hand_at_minus != flip:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
    if roll_deg:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(roll_deg), [1, 0, 0]))
    x_elbow, x_tip = target_length()
    b = m.bounds
    m.apply_scale((x_tip - x_elbow) / (b[1, 0] - b[0, 0]))
    b = m.bounds
    m.apply_translation([x_elbow - b[0, 0], -(b[0, 1] + b[1, 1]) / 2, -(b[0, 2] + b[1, 2]) / 2])
    return m


def skeleton_meshes() -> dict[str, trimesh.Trimesh]:
    """Our skeleton in the open hand, as meshes (palm, cover, fingers, thumb, motors, wrist)."""
    from mechanical.cad.drive import DriveParams, drive_parts
    from mechanical.cad.hand import Grip, PalmParams, assembled
    from mechanical.cad.wrist import WristParams, rotor, stator

    parts = assembled(PalmParams(), Grip())
    parts.update(drive_parts(DriveParams()))
    parts["wrist_rotor"], parts["wrist_stator"] = rotor(WristParams()), stator(WristParams())
    out = {}
    for name, part in parts.items():
        verts, tris = part.val().tessellate(0.3, 0.3)
        out[name] = trimesh.Trimesh([(v.x, v.y, v.z) for v in verts], [list(t) for t in tris], process=False)
    return out


def enclosure_report(shell: trimesh.Trimesh, skeleton: dict[str, trimesh.Trimesh], samples: int = 400) -> dict[str, float]:
    """Share of each skeleton part's surface points that lie outside the shell (0 = fully inside)."""
    if not shell.is_watertight:
        return {}
    out = {}
    for name, m in skeleton.items():
        pts = m.sample(samples) if len(m.faces) else m.vertices
        out[name] = round(1.0 - float(shell.contains(pts).mean()), 3)
    return out


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("model")
    ap.add_argument("--out", default="mechanical/exports/import")
    ap.add_argument("--flip", action="store_true", help="hand end is the other end")
    ap.add_argument("--roll", type=float, default=0.0, help="turn about the arm axis, degrees")
    a = ap.parse_args(argv)
    raw = load_mesh(a.model)
    shell = align(raw, a.flip, a.roll)
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    shell.export(out / "shell_aligned.stl")
    report = {
        "source": str(a.model),
        "triangles": int(len(raw.faces)),
        "watertight": bool(raw.is_watertight),
        "bodies": int(len(raw.split(only_watertight=False))),
        "aligned_bounds_mm": np.round(shell.bounds, 1).tolist(),
        "skeleton_outside_share": enclosure_report(shell, skeleton_meshes()),
    }
    if not report["watertight"]:
        report["note"] = "Mesh is not closed: enclosure check skipped; it must be repaired before hollowing."
    (out / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "skeleton_outside_share"}, indent=2))
    sticking_out = {k: v for k, v in report["skeleton_outside_share"].items() if v > 0}
    print("skeleton parts sticking out of the shell:", sticking_out or "none")
    return report


if __name__ == "__main__":
    main()
