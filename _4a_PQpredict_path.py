"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4a_PQpredict_path.py
DESCRIPTION: 
    Standardized path management for the Fan System project.
    Sets "9_Fan System" as the reference ROOT_DIR.
================================================================================
"""

import os

# 1. Project Root Directory
# Since the script is located directly inside "9_Fan System", 
# one 'dirname' is enough to set "9_Fan System" as the ROOT_DIR.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #

# 2. Input Directories (Based on your folder structure)
# Points to: 9_Fan System \ 1_Input \ 1_Blade_Parameters
FAN_DATA_DIR = os.path.join(ROOT_DIR, "1_Input", "1_Blade_Parameters") #

# 3. Define PQ Curve Model Directory
# Points to: 9_Fan System \ 1_Input \ 4_PQ_Curve_Model \ 1_Model
MODEL_DIR = os.path.join(ROOT_DIR, "1_Input", "4_PQ_Curve_Model", "1_Model") #

# 4. Output Directory
# Points to: 9_Fan System \ 2_Output \ 3_PQPredict
OUTPUT_DIR = os.path.join(ROOT_DIR, "2_Output", "3_PQPredict") #

def initialize_directories():
    """Checks and creates project directories if they don't exist.""" #
    directories = [FAN_DATA_DIR, MODEL_DIR, OUTPUT_DIR] #
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory) #
                print(f"INFO: Created directory: {directory}") #
            except Exception as e:
                print(f"ERROR: Could not create directory {directory}: {e}") #

def get_fan_json_path(fan_id):
    """Returns the full path to a blade .json file.""" #
    if not fan_id.lower().endswith(".json"):
        fan_id += ".json" #
    return os.path.join(FAN_DATA_DIR, fan_id) #

def get_model_path(model_filename):
    """Returns the full path to a specific AI model file.""" #
    return os.path.join(MODEL_DIR, model_filename) #

def get_output_path(filename):
    """Returns the full path for saving output files.""" #
    return os.path.join(OUTPUT_DIR, filename) #

# Automatically initialize folders on import
initialize_directories() #


MODEL_PATH  = os.path.join(MODEL_DIR, "fan_pq_model_weights.pth") #

SCALER_PATH = os.path.join(MODEL_DIR, "fan_scaler.joblib") #

RANDOM_STATE = 42 #

# Debug: Print the detected Root and Paths to the console
print(f"DEBUG: Current ROOT_DIR set to: {ROOT_DIR}") #
print(f"DEBUG: MODEL_PATH set to: {MODEL_PATH}") #
print(f"DEBUG: SCALER_PATH set to: {SCALER_PATH}") #