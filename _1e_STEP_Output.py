# ==================================================
# _1e_STEP_Output.py
# FINAL STABLE VERSION (Windows / Python 3.10 / pip OCP)
#
# Pipeline:
# XYZ
# -> closed polyline Wire
# -> ThruSections loft
# -> Solid
# -> STEP
#
# ❌ NO TopoDS.Edge
# ❌ NO topods_Edge
# ❌ NO BRepFill
# ❌ NO Interface_Static
# ==================================================

import os
import re

from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
)
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone


# ==================================================
# XYZ IO
# ==================================================
def _read_xyz_txt(path):
    pts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            pts.append(tuple(map(float, s.split())))
    return pts


def _pick_section_files(xyz_dir, model_name):
    pat = re.compile(rf"^{re.escape(model_name)}_Section(\d+)\.txt$", re.I)
    items = []

    for fn in os.listdir(xyz_dir):
        m = pat.match(fn)
        if m:
            items.append((int(m.group(1)), fn))

    if not items:
        raise FileNotFoundError(f"No section XYZ for {model_name}")

    items.sort()
    return [os.path.join(xyz_dir, fn) for _, fn in items]


def load_sections(xyz_dir, model_name):
    return [_read_xyz_txt(p) for p in _pick_section_files(xyz_dir, model_name)]


# ==================================================
# Geometry
# ==================================================
def _remove_duplicate_closure(pts, tol=1e-9):
    if len(pts) < 4:
        raise RuntimeError("Too few points for section")

    x0, y0, z0 = pts[0]
    x1, y1, z1 = pts[-1]

    if abs(x0 - x1) < tol and abs(y0 - y1) < tol and abs(z0 - z1) < tol:
        return pts[:-1]

    return pts


def make_closed_wire_from_pts(pts):
    pts = _remove_duplicate_closure(pts)

    wb = BRepBuilderAPI_MakeWire()

    for i in range(len(pts) - 1):
        e = BRepBuilderAPI_MakeEdge(
            gp_Pnt(*pts[i]),
            gp_Pnt(*pts[i + 1])
        ).Edge()
        wb.Add(e)

    e_close = BRepBuilderAPI_MakeEdge(
        gp_Pnt(*pts[-1]),
        gp_Pnt(*pts[0])
    ).Edge()
    wb.Add(e_close)

    if not wb.IsDone():
        raise RuntimeError("Wire build failed")

    return wb.Wire()


# ==================================================
# Loft
# ==================================================
def loft_wires(wires, make_solid=True):
    loft = BRepOffsetAPI_ThruSections(
        make_solid,   # solid
        False,        # ruled
        1e-6
    )

    for w in wires:
        loft.AddWire(w)

    loft.Build()
    if not loft.IsDone():
        raise RuntimeError("Loft failed")

    return loft.Shape()


# ==================================================
# STEP export
# ==================================================
def export_step(shape, step_path):
    os.makedirs(os.path.dirname(step_path), exist_ok=True)

    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)

    if writer.Write(step_path) != IFSelect_RetDone:
        raise RuntimeError("STEP write failed")

    print(f"[OK] STEP exported: {step_path}")
    return step_path


# ==================================================
# Public API
# ==================================================
def export_single_blade_step(
    xyz_dir,
    step_path,
    model_name,
    make_solid=True,
):
    sections = load_sections(xyz_dir, model_name)

    wires = []
    for pts in sections:
        w = make_closed_wire_from_pts(pts)
        wires.append(w)

    blade = loft_wires(wires, make_solid)
    return export_step(blade, step_path)
