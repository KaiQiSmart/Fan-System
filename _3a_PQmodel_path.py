# =========================================================
# _3a_PQmodel_path.py
#
# Purpose:
# - Centralized path management
# - All paths are relative to this file location (Dynamic)
# - Base Reference: C:\Users\RYAN.CHUANG\Desktop\Programming project\9_Fan System
# =========================================================
import os

# Get the directory where the current script is located
# Expected: C:\Users\RYAN.CHUANG\Desktop\Programming project\9_Fan System
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Define Input Root
INPUT_DIR = os.path.join(BASE_DIR, "1_Input")

# 2. Define Blade Parameters Directory (Fan Geometry Storage)
# Location: 1_Input\1_Blade_Parameters
BLADE_PARAM_DIR = os.path.join(INPUT_DIR, "1_Blade_Parameters")

# 3. Define PQ Curve Model Directory
# Location: 1_Input\4_PQ_Curve_Model
PQ_CURVE_MODEL_DIR = os.path.join(INPUT_DIR, "4_PQ_Curve_Model")

# 4. Define Sub-folders under PQ_Curve_Model
MODEL_DIR   = os.path.join(PQ_CURVE_MODEL_DIR, "1_Model")           # For .keras and .pkl
PQ_DATA_DIR  = os.path.join(PQ_CURVE_MODEL_DIR, "2_train_PQ_Data")   # For PQ JSON files
RESULT_DIR   = os.path.join(PQ_CURVE_MODEL_DIR, "3_Predic_Result")   # For output reports

# 5. Define Classified Data Sub-folders under PQ_DATA_DIR
# Based on the uploaded image structure
PQ_DATA_UNDER_50 = os.path.join(PQ_DATA_DIR, "1_under50")
PQ_DATA_50_69    = os.path.join(PQ_DATA_DIR, "2_50 to 69")
PQ_DATA_OVER_70  = os.path.join(PQ_DATA_DIR, "3_over70")

# List of all category paths for easy iteration if needed
PQ_CATEGORY_DIRS = [PQ_DATA_UNDER_50, PQ_DATA_50_69, PQ_DATA_OVER_70]

# Ensure all critical directories exist
os.makedirs(BLADE_PARAM_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PQ_DATA_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

for path in PQ_CATEGORY_DIRS:os.makedirs(path, exist_ok=True)

# Global constants for reproducibility
RANDOM_STATE = 42