# ================================================================================
# PROJECT: Fan Integrated Design Platform
# MODULE: _2a_rib_algo_params.py
# DESCRIPTION: Algorithm parameter definitions for Rib Geometry.
# ================================================================================

import json
import os

# Default Settings
SECTION_COUNT = 10

# ==================================================
# 1.X Basic
# ==================================================
MN  = "4020"         # Model Name
FW  = 50.0           # Fan Width (mm)
FH  = 15.0           # Fan Height (mm)
OD  = 92.0           # Outer Diameter (mm)
ID  = 30.0           # Inner Diameter (mm)
RC  = 7              # Rib Count
RT  = 1              # Rib Type (0=Straight, 1=Spiral)

# ==================================================
# 2.X Rib Root
# ==================================================
R_RH = 0.02          # Rib Height (mm)
R_LA = 0.4           # Leading Edge Angle (deg)
R_TW = 0.4           # Top Width (Ratio of RH) 
R_TR = 0.12          # Top Fillet Radius (Ratio of RH)
R_BW = 0.0           # Bottom Width (Ratio of RH)
R_BR = 20.0          # Bottom Fillet Radius (mm)

# ==================================================
# 3.X Rib Tip
# ==================================================
T_RH = 0.02          # Rib Height (mm)
T_LA = 0.4           # Leading Edge Angle (deg)
T_TW = 0.4           # Top Width (Ratio of RH) 
T_TR = 0.12          # Top Fillet Radius (Ratio of RH)
T_BW = 0.0           # Bottom Width (Ratio of RH)
T_BR = 20.0          # Bottom Fillet Radius (mm)

# ==================================================
# 4.X Rib_3D / Stacking Parameters
# ==================================================
FA   = 30.0          # F-angle (deg)
RAKE = 0.0           # Rake (mm)

def load_from_json(path: str):
    """
    Update global parameters from a JSON configuration file.
    """
    global MN, FW, FH, OD, ID, RC, RT
    global R_RH, R_LA, R_TW, R_TR, R_BW, R_BR
    global T_RH, T_LA, T_TW, T_TR, T_BW, T_BR
    global FA, RAKE

    if not os.path.exists(path):
        print(f"Warning: Configuration file not found at {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- 1.X Basic ---
        b = data.get("basic", {})
        MN = b.get("MN", MN)
        FW = float(b.get("FW", FW))
        FH = float(b.get("FH", FH))
        OD = float(b.get("OD", OD))
        ID = float(b.get("ID", ID))
        RC = int(b.get("RC", RC))
        RT = int(b.get("RT", RT))

        # --- 2.X Rib Root ---
        rr = data.get("rib_root", {})
        R_RH = float(rr.get("RH", R_RH))
        R_LA = float(rr.get("LA", R_LA))
        R_TW = float(rr.get("TW", R_TW))
        R_TR = float(rr.get("TR", R_TR))
        R_BW = float(rr.get("BW", R_BW))
        R_BR = float(rr.get("BR", R_BR))

        # --- 3.X Rib Tip ---
        rt = data.get("rib_tip", {})
        T_RH = float(rt.get("RH", T_RH))
        T_LA = float(rt.get("LA", T_LA))
        T_TW = float(rt.get("TW", T_TW))
        T_TR = float(rt.get("TR", T_TR))
        T_BW = float(rt.get("BW", T_BW))
        T_BR = float(rt.get("BR", T_BR))

        # --- 4.X Stacking (Matched with your JSON) ---
        # Using "rib_3d" key as per your specification
        r3d = data.get("rib_3d", {})
        
        FA   = float(r3d.get("FA", FA))
        RAKE = float(r3d.get("RAKE", RAKE))

        print(f"Successfully updated AP parameters from {path} (using 'rib_3d')")

    except Exception as e:
        print(f"Error loading JSON configuration: {e}")