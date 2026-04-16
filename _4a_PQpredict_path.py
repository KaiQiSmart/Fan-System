"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4a_PQpredict_path.py
DESCRIPTION: 
    Standardized path management. 
    Defines fixed paths for model categories (All, under50, 50-69, over70).
    Automatically detects .json, .joblib, and .pth files within these folders.
================================================================================
"""

import os
import glob

# 1. Project Root Directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Input Directories
FAN_DATA_DIR = os.path.join(ROOT_DIR, "1_Input", "1_Blade_Parameters")

# 3. Model Directory & Category Sub-folders
MODEL_BASE_DIR = os.path.join(ROOT_DIR, "1_Input", "4_PQ_Curve_Model", "1_Model")

PATH_MODEL_ALL      = os.path.join(MODEL_BASE_DIR, "0_All")
PATH_MODEL_UNDER50  = os.path.join(MODEL_BASE_DIR, "1_under50")
PATH_MODEL_50_TO_69 = os.path.join(MODEL_BASE_DIR, "2_50 to 69")
PATH_MODEL_OVER70   = os.path.join(MODEL_BASE_DIR, "3_over70")

# 4. Output Directory
OUTPUT_DIR = os.path.join(ROOT_DIR, "2_Output", "3_PQPredict")

def get_model_files_from_folder(folder_path):
    """
    Scans a specific folder and returns paths for the 3 core files.
    Returns: {'model_json': path, 'scaler_joblib': path, 'weights_pth': path}
    """
    if not os.path.exists(folder_path):
        return {"model_json": None, "scaler_joblib": None, "weights_pth": None}

    # Use glob to find files by extension (ignoring specific filenames)
    json_files   = glob.glob(os.path.join(folder_path, "*.json"))
    joblib_files = glob.glob(os.path.join(folder_path, "*.joblib"))
    pth_files    = glob.glob(os.path.join(folder_path, "*.pth"))

    return {
        "model_json":    json_files[0]   if json_files   else None,
        "scaler_joblib": joblib_files[0] if joblib_files else None,
        "weights_pth":   pth_files[0]    if pth_files    else None
    }

def get_fan_json_path(fan_id):
    """Returns the full path to a blade .json file."""
    if not fan_id.lower().endswith(".json"):
        fan_id += ".json"
    return os.path.join(FAN_DATA_DIR, fan_id)

def get_output_path(filename):
    """Returns the full path for saving output files."""
    return os.path.join(OUTPUT_DIR, filename)

def initialize_directories():
    """Checks and creates project base directories if they don't exist."""
    directories = [FAN_DATA_DIR, MODEL_BASE_DIR, OUTPUT_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

# Initialize base folders
initialize_directories()