# ================================================================================
# PROJECT: Fan Integrated Design Platform
# MODULE: _2d_XYZ_Output.py
# DESCRIPTION:
#   XYZ output module for Trapezoidal Rib System (Clean Version)
#   - Generates spanwise rib sections
#   - Ensures high-precision coordinate output (: .8f)
#   - Enforces point-to-point distance tolerance for CAD kernels
# ================================================================================

import os
import numpy as np
from math import cos, sin, pi, sqrt

import _2a_rib_algo_params as AP
from _2c_3D_Rib import get_section_params, map_2d_to_3d
from _2b_2D_Rib import generate_rib_2d


class RibXYZGenerator:
    """
    Core Generator for Rib XYZ datasets.
    XYZ is the SINGLE SOURCE OF TRUTH for all CAD/CFD operations.
    """

    def __init__(self):
        # Model Name from AP
        self.MN = str(AP.MN)
        # Number of sections along the span (Default to 10)
        self.N = int(getattr(AP, "SECTION_COUNT", 10))

    def export_xyz(self, out_dir: str):
        """
        Generates and saves closed-loop XYZ files for each section.
        """
        os.makedirs(out_dir, exist_ok=True)
        
        # Tolerance for closing the loop (CAD specific)
        TOLERANCE = 1e-4

        for i in range(self.N):
            # t = [0.0 (Root) ... 1.0 (Tip)]
            t = i / (self.N - 1) if self.N > 1 else 0.0

            # 1. Get interpolated parameters for this layer
            p = get_section_params(t)

            # 2. Generate 2D geometry (includes internal distance filtering)
            pts_2d = generate_rib_2d(
                RH=p["RH"],
                LA=p["LA"],
                TW=p["TW"],
                BW=p["BW"],
                TR=p["TR"],
                BR=p["BR"],
                steps=64 # Optimized for SolidWorks curve stability
            )

            # 3. Map 2D points to 3D cylindrical space
            pts_3d = map_2d_to_3d(
                pts_2d,
                p["R"],
                p["FA"],
                p["Z_offset"]
            )

            # 4. FINAL TOPOLOGICAL CLOSURE
            # SolidWorks 'Curve through XYZ points' requires a precise loop
            if len(pts_3d) > 2:
                p_start = np.array(pts_3d[0])
                p_end = np.array(pts_3d[-1])
                dist = sqrt(np.sum((p_start - p_end)**2))
                
                # Only add start point to end if they are not already identical
                if dist > TOLERANCE:
                    pts_3d.append(pts_3d[0])
                else:
                    # Force exact identity for the last point to ensure closure
                    pts_3d[-1] = pts_3d[0]

            # 5. Save to Text File
            fn = f"{self.MN}_RibSection{i}.txt"
            path = os.path.join(out_dir, fn)

            with open(path, "w", encoding="utf-8") as f:
                for x, y, z in pts_3d:
                    # Use 8 decimal places to avoid rounding collisions
                    f.write(f"{x:.8f} {y:.8f} {z:.8f}\n")

        print(f"[XYZ] Exported {self.N} sections to: {out_dir}")


def rotate_ribs(out_dir: str, rib_count: int):
    """
    Generates a circular array of ribs based on the generated base sections.
    """
    if rib_count <= 1:
        return

    # Find base files (files NOT starting with a number)
    base_files = [
        f for f in os.listdir(out_dir)
        if f.endswith(".txt") and "RibSection" in f and not f[0].isdigit()
    ]

    if not base_files:
        return

    dtheta = 2.0 * pi / rib_count

    for i in range(rib_count):
        angle = i * dtheta
        c, s = cos(angle), sin(angle)

        for fn in base_files:
            src = os.path.join(out_dir, fn)
            # Prefix with rib index (e.g., 1_Model_Section0.txt)
            dst = os.path.join(out_dir, f"{i+1}_{fn}")

            # Use numpy for fast loading
            data = np.loadtxt(src)
            if data.ndim == 1:
                data = data.reshape(1, -1)

            rotated_pts = []
            for x, y, z in data:
                # Rotate around Z-axis
                xr = x * c - y * s
                yr = x * s + y * c
                rotated_pts.append((xr, yr, z))

            # Re-enforce closure identity after rotation math
            if len(rotated_pts) > 1:
                rotated_pts[-1] = rotated_pts[0]

            with open(dst, "w", encoding="utf-8") as f:
                for rx, ry, rz in rotated_pts:
                    f.write(f"{rx:.8f} {ry:.8f} {rz:.8f}\n")

    # Clean up original unrotated files
    for fn in base_files:
        try:
            os.remove(os.path.join(out_dir, fn))
        except:
            pass

    print(f"[ROTATE] Array generation complete for {rib_count} ribs.")


def rotate_ribs_with_prefix(out_dir: str, rib_count: int):
    """GUI entry point."""
    rotate_ribs(out_dir, rib_count)