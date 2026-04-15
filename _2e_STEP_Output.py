import os
import re
import traceback
import math

# --- OCP Imports ---
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax1, gp_Ax2, gp_Trsf, gp_Vec
from OCP.TopAbs import TopAbs_WIRE, TopAbs_FACE, TopAbs_EDGE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge, 
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_Transform
)
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepFill import BRepFill_Filling
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.GeomAbs import GeomAbs_C2, GeomAbs_C0

# --- Centralized Paths ---
try:
    from _2a_rib_path import STEP_DIR, XYZ_ROOT_DIR
except ImportError:
    STEP_DIR = "./"
    XYZ_ROOT_DIR = "./"

# ================================================================================
# HELPERS
# ================================================================================

def _read_xyz_txt(path, shift_to_center=0.0):
    pts = []
    if not os.path.exists(path): return pts
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s: continue
            try:
                raw_pt = list(map(float, s.split()))
                if shift_to_center > 0:
                    x, y, z = raw_pt
                    dist = math.sqrt(x**2 + y**2)
                    if dist > 1e-6:
                        # Ensures the rib root slightly penetrates the hub
                        ratio = (dist - shift_to_center) / dist
                        raw_pt = [x * ratio, y * ratio, z]
                pts.append(tuple(raw_pt))
            except ValueError: continue
    return pts

def make_non_planar_face_from_pts(pts):
    if len(pts) < 3: return None
    wb = BRepBuilderAPI_MakeWire()
    tol = 1e-8
    is_closed = gp_Pnt(*pts[0]).Distance(gp_Pnt(*pts[-1])) < tol
    active_pts = pts[:-1] if is_closed else pts
    for i in range(len(active_pts)):
        p1 = gp_Pnt(*active_pts[i])
        p2 = gp_Pnt(*active_pts[(i + 1) % len(active_pts)])
        if p1.Distance(p2) > tol:
            wb.Add(BRepBuilderAPI_MakeEdge(p1, p2).Edge())
    if not wb.IsDone(): return None
    wire = wb.Wire()
    filler = BRepFill_Filling()
    edge_exp = TopExp_Explorer(wire, TopAbs_EDGE)
    while edge_exp.More():
        filler.Add(TopoDS.Edge_s(edge_exp.Current()), GeomAbs_C0, True)
        edge_exp.Next()
    filler.Build()
    return filler.Face() if filler.IsDone() else None

# ================================================================================
# MAIN ENTRY POINT (export_rib_step)
# ================================================================================

def export_rib_step(model_name, fan_params=None):
    """
    Called by _2_rib_GUI.py.
    Generates:
    1. 1_{model_name}_Rib.step (Single Blade)
    2. 1_{model_name}_FullFan.step (Multi-body Assembly)
    """
    try:
        source_dir = XYZ_ROOT_DIR
        output_dir = STEP_DIR
        
        # 1. Identify section files
        pat = re.compile(rf"^1_{re.escape(model_name)}_RibSection(\d+)\.txt$", re.I)
        files = sorted([f for f in os.listdir(source_dir) if pat.match(f)], 
                       key=lambda x: int(pat.match(x).group(1)))
        
        if len(files) < 2: return False, "Missing RibSection files."

        section_wires = []
        section_faces = []

        for i, f_name in enumerate(files):
            # Move root (Section 0) 0.1mm towards center
            if i == 0:                     # Ensures better sewing with the hub, eliminating tiny gaps that cause STEP import failures
                shift = 0.02
            elif i == len(files) - 1:  
                shift = -0.02                 #-0.02  Optional: Slightly shift tip inward to improve lofting stability (can be adjusted or removed based on results)
            else: 
                shift = 0.0

            pts = _read_xyz_txt(os.path.join(source_dir, f_name), shift_to_center=shift)
            face = make_non_planar_face_from_pts(pts)
            if face:
                section_faces.append(face)
                exp = TopExp_Explorer(face, TopAbs_WIRE)
                if exp.More(): section_wires.append(TopoDS.Wire_s(exp.Current()))

        # --- Generate Single Rib Solid ---
        builder = BRepOffsetAPI_ThruSections(False, False, 1e-8)
        builder.SetContinuity(GeomAbs_C2)
        for w in section_wires: builder.AddWire(w)
        builder.CheckCompatibility(False)
        builder.Build()
        
        sewer = BRepBuilderAPI_Sewing(1e-5)
        sewer.Add(builder.Shape())
        sewer.Add(section_faces[0])
        sewer.Add(section_faces[-1])
        sewer.Perform()
        
        single_rib = sewer.SewedShape()
        shell_exp = TopExp_Explorer(single_rib, TopAbs_SHELL)
        if shell_exp.More():
            sm = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(shell_exp.Current()))
            if sm.IsDone(): single_rib = sm.Solid()

        # Save Single Rib STEP
        rib_path = os.path.join(output_dir, f"1_{model_name}_Rib.step")
        writer_single = STEPControl_Writer()
        writer_single.Transfer(single_rib, STEPControl_AsIs)
        writer_single.Write(rib_path)

        # --- Generate Full Fan Assembly (Multi-body) ---
        if fan_params:
            writer_full = STEPControl_Writer()
            
            # (A) Hub Cylinder
            hub_r = fan_params.get('ID', 0) / 2.0
            hub_h = fan_params.get('R_RH', 0)
            hub = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), hub_r, hub_h).Solid()
            writer_full.Transfer(hub, STEPControl_AsIs)
            
            # (B) Frame
            fw, fh = fan_params.get('FW', 0), fan_params.get('FH', 0)
            od_r = fan_params.get('OD', 0) / 2.0
            box = BRepPrimAPI_MakeBox(gp_Pnt(-fw/2, -fw/2, 0), fw, fw, fh).Solid()
            hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), od_r, fh).Solid()
            frame = BRepAlgoAPI_Cut(box, hole).Shape()
            writer_full.Transfer(frame, STEPControl_AsIs)
            
            # (C) Arrayed Blades
            rc = int(fan_params.get('RC', 1))
            for i in range(rc):
                trsf = gp_Trsf()
                trsf.SetRotation(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(0,0,1)), (2.0 * math.pi * i) / rc)
                rotated_rib = BRepBuilderAPI_Transform(single_rib, trsf).Shape()
                writer_full.Transfer(rotated_rib, STEPControl_AsIs)
            
            # Save Full Fan STEP
            full_path = os.path.join(output_dir, f"1_{model_name}_FullFan.step")
            if writer_full.Write(full_path) == IFSelect_RetDone:
                return True, f"Success:\n1. {rib_path}\n2. {full_path}"
            else:
                return False, "Failed to write FullFan STEP."

        return True, rib_path

    except Exception as e:
        traceback.print_exc()
        return False, str(e)