import os
import re
import traceback

# --- OCP Imports ---
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_WIRE, TopAbs_FACE, TopAbs_EDGE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge, 
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_MakeSolid
)
from OCP.BRepFill import BRepFill_Filling
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.ShapeFix import ShapeFix_Shape, ShapeFix_Solid
from OCP.GeomAbs import GeomAbs_C2, GeomAbs_C0

# --- Centralized Paths ---
try:
    from _2a_rib_path import STEP_DIR, XYZ_ROOT_DIR
except ImportError:
    STEP_DIR = "./"
    XYZ_ROOT_DIR = "./"

def _read_xyz_txt(path):
    pts = []
    if not os.path.exists(path): return pts
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s: continue
            try:
                pts.append(tuple(map(float, s.split())))
            except ValueError: continue
    return pts

def make_non_planar_face_from_pts(pts):
    """
    Creates high-fidelity non-planar faces.
    Using C0 to keep the boundary strictly matched to points.
    """
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

def export_rib_step(model_name):
    """
    Eliminates segmentation lines (steps) by using smooth lofting (Ruled=False)
    while maintaining point fidelity via SetContinuity and CheckCompatibility(False).
    """
    try:
        source_dir = XYZ_ROOT_DIR
        output_dir = STEP_DIR
        pat = re.compile(rf"^1_{re.escape(model_name)}_RibSection(\d+)\.txt$", re.I)
        files = sorted([f for f in os.listdir(source_dir) if pat.match(f)], 
                       key=lambda x: int(pat.match(x).group(1)))
        
        if len(files) < 2: return False, "Insufficient files."

        section_wires = []
        section_faces = []
        
        for f_name in files:
            pts = _read_xyz_txt(os.path.join(source_dir, f_name))
            face = make_non_planar_face_from_pts(pts)
            if face:
                section_faces.append(face)
                wire_exp = TopExp_Explorer(face, TopAbs_WIRE)
                if wire_exp.More():
                    section_wires.append(TopoDS.Wire_s(wire_exp.Current()))

        # --- KEY CHANGE: SMOOTH LOFTING ---
        # 1. ruled=False: Uses B-Splines to smooth out the transition between sections.
        # 2. pres3d=1e-8: Keeps the surface extremely close to the input wires.
        builder = BRepOffsetAPI_ThruSections(False, False, 1e-8)
        
        # 3. SetContinuity(GeomAbs_C2): Ensures curvature continuity (no visible edges).
        builder.SetContinuity(GeomAbs_C2) 
        
        for w in section_wires:
            builder.AddWire(w)
        
        # 4. CheckCompatibility(False): Critical to keep the section points aligned 
        # as-is without software re-interpolation (prevents shrinking).
        builder.CheckCompatibility(False)
        builder.Build()
        
        if not builder.IsDone(): return False, "Smooth lofting failed."
        side_walls = builder.Shape()

        # Final Sewing and Solidification
        sewer = BRepBuilderAPI_Sewing(1e-6)
        sewer.Add(side_walls)
        sewer.Add(section_faces[0])
        sewer.Add(section_faces[-1])
        sewer.Perform()
        
        sewed_result = sewer.SewedShape()
        final_output = sewed_result

        if sewed_result.ShapeType() != TopAbs_SOLID:
            shell_exp = TopExp_Explorer(sewed_result, TopAbs_SHELL)
            if shell_exp.More():
                sm = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(shell_exp.Current()))
                if sm.IsDone(): final_output = sm.Solid()

        step_path = os.path.join(output_dir, f"1_{model_name}_Rib.step")
        writer = STEPControl_Writer()
        writer.Transfer(final_output, STEPControl_AsIs)
        
        if writer.Write(step_path) == IFSelect_RetDone:
            return True, step_path
        return False, "Export failed."

    except Exception as e:
        traceback.print_exc()
        return False, str(e)