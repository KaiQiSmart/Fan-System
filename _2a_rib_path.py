# ==================================================
# _2a_rib_path.py
# Centralized path management for Fan System
#
# Purpose:
# - Define ALL filesystem paths used in the system
# - Serve as a path index (who uses what)
#
# Rule:
# - NO other module is allowed to hard-code paths
# - All paths must be defined and documented here
# ==================================================

import os


# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------
# Input / JSON (Blade parameters)
#
# Structure:
# 1_Input/
# └─ 1_Blade_Parameters/
#
# Used by:
# - _1_fan_GUI.py (Load / Save JSON)
# --------------------------------------------------
INPUT_DIR = os.path.join(PROJECT_ROOT, "1_Input")
JSON_DIR  = os.path.join(INPUT_DIR, "2_Rib_Parameters")


# --------------------------------------------------
# Output root directory
#
# Structure:
# 2_Output/
#
# Used by:
# - Geometry
# - Viewer
# - STEP
# --------------------------------------------------
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "2_Output","2_Rib")


# --------------------------------------------------
# XYZ Output (SolidWorks reference)
#
# Structure:
# 2_Output/Solidworks/
# ├─ 0/   (base blade, city reference)
# ├─ 1/
# ├─ 2/
# └─ ...
#
# Used by:
# - _1_fan_GUI.generate_xyz()
# - _1d_XYZ_Output.export_xyz()
# - rotate_xyz_with_prefix()
# --------------------------------------------------
XYZ_ROOT_DIR = os.path.join(OUTPUT_DIR, "1_Solidworks_XYZ")
XYZ_CREO_DIR = os.path.join(OUTPUT_DIR, "2_Creo_XYZ")

def xyz_base_dir():
    """
    Base XYZ directory (city reference / original blade)

    Used by:
    - _1_fan_GUI.generate_xyz()
    - _1d_XYZ_Output.export_xyz()
    """
    return XYZ_ROOT_DIR


def xyz_rotated_dir(index: int):
    """
    Rotated XYZ directories: 1, 2, 3, ...

    Used by:
    - rotate_xyz_with_prefix() (future folder-based version)
    """
    return os.path.join(XYZ_ROOT_DIR, str(index))


# --------------------------------------------------

# --------------------------------------------------
STEP_DIR = os.path.join(OUTPUT_DIR, "3_Step_3D")


# --------------------------------------------------
# Viewer Output (Fan Shape / Envelope Preview)
#
# Structure:
# 2_Output/Viewer/
#
# Used by:
# - _1f_Blade_Viewer.py
# - _1_fan_GUI.py (preview refresh / save image)
# --------------------------------------------------
VIEWER_DIR = os.path.join(OUTPUT_DIR, "Viewer")


def viewer_dir():
    """
    Fan shape viewer output directory

    Used by:
    - _1f_Blade_Viewer
    """
    return VIEWER_DIR




# --------------------------------------------------
# Utility
#
# Used by:
# - _1_fan_GUI.__init__()
# --------------------------------------------------
def ensure_dirs():
    """
    Ensure all required directories exist
    """
    dirs = [
        INPUT_DIR,
        JSON_DIR,
        OUTPUT_DIR,
        XYZ_ROOT_DIR,
        XYZ_CREO_DIR,
        VIEWER_DIR,
        STEP_DIR,
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)
