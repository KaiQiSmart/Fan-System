"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _1d_XYZ_Output.py
DESCRIPTION: 
    JSON-driven blade generator (XYZ ONLY).
    Updates: 
    - Support for Split H (Root H and Tip H).
    - Alternating Bump Logic: Odd sections have Bump, Even sections are plain.
================================================================================
"""

import os
import json
from math import pi, cos, sin, tan
import re

import _1a_fan_algo_params as AP

from _1c_3D_Blade import (
    X_2_U, Y_2_U, Z_2_U,
    X_2_L, Y_2_L, Z_2_L,
    Fang_transf
)

# ==================================================
# Geometry utilities
# ==================================================

def distance3d(p, q):
    """Calculate the Euclidean distance between two 3D points."""
    return ((p[0] - q[0])**2 + (p[1] - q[1])**2 + (p[2] - q[2])**2) ** 0.5


def connect_two_curves(points1, points2, tol=1e-3):
    """Connect upper and lower airfoil points into a closed loop."""
    if len(points1) < 2 or len(points2) < 2:
        raise ValueError("Each curve must contain at least two points.")

    p1_start, p1_end = points1[0], points1[-1]
    p2_start, p2_end = points2[0], points2[-1]

    combos = [
        ("p1_start", "p2_start", distance3d(p1_start, p2_start)),
        ("p1_start", "p2_end",   distance3d(p1_start, p2_end)),
        ("p1_end",   "p2_start", distance3d(p1_end,   p2_start)),
        ("p1_end",   "p2_end",   distance3d(p1_end,   p2_end)),
    ]
    combos.sort(key=lambda x: x[2])
    label1, label2, _ = combos[0]

    if label1 == "p1_start" and label2 == "p2_start":
        points1 = list(reversed(points1))
    elif label1 == "p1_start" and label2 == "p2_end":
        points1 = list(reversed(points1))
        points2 = list(reversed(points2))
    elif label1 == "p1_end" and label2 == "p2_end":
        points2 = list(reversed(points2))

    combined = list(points1) + list(points2[1:])

    if distance3d(combined[0], combined[-1]) > tol:
        combined.append(combined[0])

    return combined


# ==================================================
# Blade Generator (XYZ generation)
# ==================================================

class BladeGenerator:
    def __init__(self, json_path: str, inverted: bool = False):
        self.json_path = json_path
        self.nor_or_inv = -1 if inverted else 1
        self._load_config()

    def _load_config(self):
        """Load configuration from JSON with support for Split H."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(self.json_path)

        with open(self.json_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        b = cfg["basic"]
        self.MN = b["MN"]
        self.BC = int(b["BC"])
        self.ID = float(b["ID"])
        self.OD = float(b["OD"])

        self.root = cfg["airfoil_root"]
        self.tip  = cfg["airfoil_tip"]

        self.H_root = float(self.root.get("CH", 6.55))
        self.H_tip  = float(self.tip.get("CH", 6.55))

        d3 = cfg["blade_3d"]
        self.FA   = float(d3["FA"])
        self.S    = float(d3["S"])
        
        wave_params = d3.get("Wave", [0.0, 1.0])
        self.WAVE_PCT   = float(wave_params[0])
        self.WAVE_COUNT = float(wave_params[1])
        self.RISE_ANG   = float(d3.get("Rise", 0.0))

        # Algorithm Settings (Base parameters from AP)
        self.N = int(getattr(AP, "SECTION_COUNT", 10))
        
        # Load base bump parameters with safety for U3/L3
        self.base_u = [
            float(getattr(AP, "U1", 0.0)),
            float(getattr(AP, "U2", 0.0)),
            float(getattr(AP, "U3", 1.0))
        ]
        self.base_l = [
            float(getattr(AP, "L1", 0.0)),
            float(getattr(AP, "L2", 0.0)),
            float(getattr(AP, "L3", 1.0))
        ]

    @staticmethod
    def _lerp(a, b, t):
        """Linear interpolation."""
        return a * (1.0 - t) + b * t

    def export_xyz(self, out_dir: str, n_points: int = 61):
        """Generate XYZ files with Alternating Bump Logic."""
        os.makedirs(out_dir, exist_ok=True)

        Fold = 0.0
        z_offset_base = 0.0

        for i in range(self.N):
            t = i / (self.N - 1)

            # --- 1. Modified Bump Logic (Trigger on 2, 4, 6, 8...) ---
            # i=0 or Odd (1, 3, 5...) -> Plain airfoil
            # i=2, 4, 6, 8...        -> Airfoil with Bump
            if i > 0 and i % 2 == 0:
                current_u = self.base_u
                current_l = self.base_l
                bump_status = "ON"
            else:
                current_u = [0.0, 0.0, 1.0]
                current_l = [0.0, 0.0, 1.0]
                bump_status = "OFF"

            # 2. Parameter Interpolation
            D   = self._lerp(self.ID, self.OD, t)
            H_i = self._lerp(self.H_root, self.H_tip, t) 
            
            M   = self._lerp(self.root["CAM"], self.tip["CAM"], t)
            P   = self._lerp(self.root["CP"],  self.tip["CP"],  t)
            T   = self._lerp(self.root["TM"],  self.tip["TM"],  t)
            TT  = self._lerp(self.root["TTE"], self.tip["TTE"], t)
            Aoi = self._lerp(self.root["IA"],  self.tip["IA"],  t)
            L   = self._lerp(self.root["LEO"], self.tip["LEO"], t)

            chord = H_i / sin(Aoi * pi / 180.0)
            T_rel  = 100.0 * T  / chord
            TT_rel = 100.0 * TT / chord

            D0 = D if i == 0 else self._lerp(self.ID, self.OD, (i - 1) / (self.N - 1))

            # 3. Stacking & Z-Modulation
            dz_rise = (D/2.0 - self.ID/2.0) * tan(self.RISE_ANG * pi / 180.0)
            wave_amplitude = H_i * (self.WAVE_PCT / 100.0)
            dz_wave = wave_amplitude * sin(2 * pi * t * self.WAVE_COUNT) if i > 0 else 0.0
            total_dz = dz_rise + dz_wave

            # 4. Points Generation
            upper_pts, lower_pts = [], []
            for j in range(n_points):
                beta = pi * j / (n_points - 1)
                x = 0.5 * (1 - cos(beta))

                upper_pts.append((
                    X_2_U(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, Fold, self.S, current_u[0], current_u[1], current_u[2]),
                    Y_2_U(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, Fold, self.S, current_u[0], current_u[1], current_u[2]),
                    self.nor_or_inv * Z_2_U(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, self.S, current_u[0], current_u[1], current_u[2]),
                ))

                lower_pts.append((
                    X_2_L(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, Fold, self.S, current_l[0], current_l[1], current_l[2]),
                    Y_2_L(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, Fold, self.S, current_l[0], current_l[1], current_l[2]),
                    self.nor_or_inv * Z_2_L(x, M, P, T_rel, TT_rel, D, Aoi, L, H_i, self.FA, D0, self.S, current_l[0], current_l[1], current_l[2]),
                ))

            closed_pts = connect_two_curves(upper_pts, lower_pts)

            if i == 0:
                z_offset_base = min(p[2] for p in closed_pts)

            final_pts = [(px, py, (pz - z_offset_base) + total_dz) for (px, py, pz) in closed_pts]

            # 5. Save to Disk
            fn = f"{self.MN}_Section{i}.txt"
            with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as f:
                for px, py, pz in final_pts:
                    f.write(f"{px:.6f} {py:.6f} {pz:.6f}\n")

            Fold += Fang_transf(D, self.FA, D0)
            print(f"[XYZ] {fn} | Bump: {bump_status} | H: {H_i:.3f}")


# ==================================================
# XYZ rotation (Prefix-based)
# ==================================================

def rotate_xyz_with_prefix(xyz_dir: str, blade_count: int):
    """Clean old files, rotate sections around Z, and add 1_, 2_, ... prefixes."""
    pattern = re.compile(r"^\d+_.*_section\d+\.txt$", re.IGNORECASE)
    
    for fn in os.listdir(xyz_dir):
        if pattern.match(fn):
            try: os.remove(os.path.join(xyz_dir, fn))
            except: pass

    base_files = [
        f for f in os.listdir(xyz_dir)
        if f.lower().endswith(".txt") and "_section" in f.lower() and not f[0].isdigit()
    ]

    if not base_files:
        return

    dtheta = 360.0 / blade_count
    for i in range(blade_count):
        rad = (i * dtheta) * pi / 180.0
        c, s = cos(rad), sin(rad)

        for fn in base_files:
            src = os.path.join(xyz_dir, fn)
            dst = os.path.join(xyz_dir, f"{i+1}_{fn}")

            with open(src, "r", encoding="utf-8") as f:
                pts = [tuple(map(float, line.split())) for line in f]

            with open(dst, "w", encoding="utf-8") as f:
                for x, y, z in pts:
                    xr = x * c - y * s
                    yr = x * s + y * c
                    f.write(f"{xr:.6f} {yr:.6f} {z:.6f}\n")

    for fn in base_files:
        try: os.remove(os.path.join(xyz_dir, fn))
        except: pass
    print(f"[ROTATE] Finished rotating {blade_count} blades.")