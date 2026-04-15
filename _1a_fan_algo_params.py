"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _1a_fan_algo_params.py
DESCRIPTION: 
    Algorithm parameter definitions and JSON loader.
    Updates: Support for Split H (Root/Tip), Percentage-based Wave, and Rise.
================================================================================
"""

# NACA base coefficients (Standard open trailing edge)
_A0 = 0.2969
_A1 = -0.1260
_A2 = -0.3516
_A3 = 0.2843
_A4 = -0.1036



# Number of sections generated from Root to Tip (Default: 10)
SECTION_COUNT = 10

# ==================================================
# 1.X Basic Specifications
# ==================================================
MN  = "4020"         # 1.1 Model Name
FW  = 50.0           # 1.2 Fan Width (mm)
FH  = 15.0           # 1.3 Fan Height (mm)
OD  = 92.0           # 1.4 Outer Diameter (mm)
ID  = 30.0           # 1.5 Inner Diameter (mm)
HH  = 10.0           # Hub Height (mm) - New parameter for hub geometry
BC  = 7              # 1.6 Blade Count
CG  = 0.5            # 1.7 Clearance Gap (mm)
RPM = 4800           # 1.8 Rated Speed (rpm)

# ==================================================
# 2.X Airfoil_Tip (Tip Section)
# ==================================================
T_CH   = 6.55         # 2.1 Chord Height (mm)    ChordLength = H / sin(IA) 
T_CAM = 0.02         # 2.2 Camber (ratio)
T_CP  = 0.4          # 2.3 Camber Position (ratio)
T_TM  = 0.12         # 2.4 Max Thickness (mm)
T_TTE = 0.0          # 2.5 Trailing-Edge Thickness (mm)
T_IA  = 20.0         # 2.6 Angle of Incidence (deg)
T_LEO = 0.0          # 2.7 Leading Edge Offset (mm)

# ==================================================
# 3.X Airfoil_Root (Root Section)
# ==================================================
R_CH   = 6.55         # 3.1 Chord Height (mm)    ChordLength = H / sin(IA) 
R_CAM = 0.02         # 3.2 Camber (ratio)
R_CP  = 0.4          # 3.3 Camber Position (ratio)
R_TM  = 0.12         # 3.4 Max Thickness (mm)
R_TTE = 0.0          # 3.5 Trailing-Edge Thickness (mm)
R_IA  = 20.0         # 3.6 Angle of Incidence (deg)
R_LEO = 0.0          # 3.7 Leading Edge Offset (mm)

# ==================================================
# 4.X Blade_3D / Stacking Parameters
# ==================================================
FA   = 30.0          # 4.1 F-angle (deg): Forward/Backward Sweep
S    = 10.0          # 4.2 Blade Sharpness (Larger = Sharper)
WAVE = [0.0, 1.0]    # 4.3 Stacking Wave: [Amplitude % of H, Number of Cycles]
RISE = 0.0           # 4.4 Rise Angle (deg): Linear vertical tilt (Dihedral)
U_BUMP = [0.0, 0.0, 1.0]   # 4.5 Upper Surface Bump Parameters (U1, U2, U3)(Amplitude0~1, Location0~1, Width0~2)    
L_BUMP = [0.0, 0.0, 1.0]   # 4.6 Lower Surface Bump Parameters (L1, L2, L3)(Amplitude0~1, Location0~1, Width0~2)

# --- Individual Bump Variables (For direct access) ---
U1 = 0.0; U2 = 0.0; U3 = 1.0
L1 = 0.0; L2 = 0.0; L3 = 1.0

# ==================================================
# Airfoil Surface Bump Parameters (Advanced)
# ==================================================
# Upper Surface Bump
#U1 = 0.0        # Bump height (Amplitude)
#U2 = 0.0        # Bump location (Normalized 0-1)
#U3 = 1.0        # Bump width (Cannot be 0)

# Lower Surface Bump
#L1 = 0.0        # Bump height (Amplitude)
#L2 = 0.0        # Bump location (Normalized 0-1)
#L3 = 1.0        # Bump width (Cannot be 0)


# ==================================================
# JSON Loader Logic
# ==================================================
def load_from_json(path: str):
    import json
    import os

    # Declare global variables to be updated
    global MN, FW, FH, OD, ID,HH, BC, CG, RPM
    global T_CH, T_CAM, T_CP, T_TM, T_TTE, T_IA, T_LEO
    global R_CH, R_CAM, R_CP, R_TM, R_TTE, R_IA, R_LEO
    global FA, S, WAVE, RISE, U_BUMP, L_BUMP
    global U1, U2, U3, L1, L2, L3  # Add these to update globally

    if not os.path.exists(path):
        print(f"[Warning] Config path {path} not found. Using defaults.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- 1.X Basic ---
    b = data.get("basic", {})
    MN  = b.get("MN", MN)
    FW  = b.get("FW", FW)
    FH  = b.get("FH", FH)
    OD  = b.get("OD", OD)
    ID  = b.get("ID", ID)
    HH  = b.get("HH", HH)
    BC  = b.get("BC", BC)
    CG  = b.get("CG", CG)
    RPM = b.get("RPM", RPM)

    # --- 2.X Airfoil_Tip ---
    t = data.get("airfoil_tip", {})
    T_CH  = t.get("CH",  T_CH)
    T_CAM = t.get("CAM", T_CAM)
    T_CP  = t.get("CP",  T_CP)
    T_TM  = t.get("TM",  T_TM)
    T_TTE = t.get("TTE", T_TTE)
    T_IA  = t.get("IA",  T_IA)
    T_LEO = t.get("LEO", T_LEO)

    # --- 3.X Airfoil_Root ---
    r = data.get("airfoil_root", {})
    R_CH  = r.get("CH",  R_CH)
    R_CAM = r.get("CAM", R_CAM)
    R_CP  = r.get("CP",  R_CP)
    R_TM  = r.get("TM",  R_TM)
    R_TTE = r.get("TTE", R_TTE)
    R_IA  = r.get("IA",  R_IA)
    R_LEO = r.get("LEO", R_LEO)

    # --- 4.X Blade_3D / Stacking ---
    d3 = data.get("blade_3d", {})
    FA   = d3.get("FA", FA)
    S    = d3.get("S",  S)
    WAVE = d3.get("Wave", WAVE)
    RISE = d3.get("Rise", RISE)
    
    # Directly read the list, and if it is missing in the JSON, assign the default value [0.0, 0.0, 1.0].
    U_BUMP = d3.get("U_Bump", [0.0, 0.0, 1.0])
    L_BUMP = d3.get("L_Bump", [0.0, 0.0, 1.0])

    #  (U1, U2, U3 / L1, L2, L3)
    U1, U2, U3 = U_BUMP
    L1, L2, L3 = L_BUMP

    print(f"[Config] Loaded Bump Params -> U:[{U1},{U2},{U3}], L:[{L1},{L2},{L3}]")