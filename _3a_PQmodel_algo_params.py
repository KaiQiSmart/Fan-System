"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _3a_PQmodel_algo_params.py
PURPOSE: Define feature sequence, model hyperparameters, and data split ratios.
================================================================================
"""

"""
================================================================================
{
  "basic_info": {
    "blade_model": "A8020 NEW_7B.json", // Model identifier (matches the .json file name in the blade parameters)
    "speed_rpm": 2000,                  // Operating speed for PQ curve prediction rpm
    "data_source": null,                //"measured / simulated / null"
    "test_conditions": null,            //"Condition file name  / null"
    "upload_date": 2026/4/15            // "YYYY/MM/DD" format, can be auto-generated on upload
  },
  "test_data": {
    "pq_curve": [
      { "idx": 1, "P": 2.133, "Q": 0.000 },
      { "idx": 2, "P": 0.665, "Q": 9.933 },
      { "idx": 3, "P": 0.625, "Q": 12.191 },
      { "idx": 4, "P": 0.506, "Q": 14.100 },
      { "idx": 5, "P": 0.000, "Q": 17.272 }
    ],
    "noise_dba": null
  }
}
================================================================================
"""

# 1. Data Split Ratios
# Define the percentage allocation for the training set (Train), validation set (Val), and test set (Test)
TRAIN_RATIO = 70 
VAL_RATIO   = 10 
TEST_RATIO  = 20 

# Model Hyperparameters (Fix: Add DEFAULT_EPOCHS required by the GUI)
DEFAULT_EPOCHS = 100
BATCH_SIZE = 8
LEARNING_RATE = 0.001

FEATURE_ORDER = [
    # =========================
    # Basic
    # =========================
    "geo_base_FW",     # basic.FW
    "geo_base_FH",     # basic.FH
    "geo_base_OD",     # basic.OD
    "geo_base_ID",     # basic.ID
    "geo_base_HH",     # basic.HH
    "geo_base_BC",     # basic.BC
    "geo_base_CG",     # basic.CG

    # =========================
    # Operating Condition
    # =========================
    "cond_operating_rpm",   # conditions.speed_rpm (PQ operating speed)

    # =========================
    # Airfoil Root
    # =========================
    "geo_root_CH",     # airfoil_root.CH
    "geo_root_CAM",    # airfoil_root.CAM
    "geo_root_CP",     # airfoil_root.CP
    "geo_root_TM",     # airfoil_root.TM
    "geo_root_TTE",    # airfoil_root.TTE
    "geo_root_IA",     # airfoil_root.IA
    "geo_root_LEO",    # airfoil_root.LEO

    # =========================
    # Airfoil Tip
    # =========================
    "geo_tip_CH",      # airfoil_tip.CH
    "geo_tip_CAM",     # airfoil_tip.CAM
    "geo_tip_CP",     # airfoil_tip.CP
    "geo_tip_TM",     # airfoil_tip.TM
    "geo_tip_TTE",    # airfoil_tip.TTE
    "geo_tip_IA",     # airfoil_tip.IA
    "geo_tip_LEO",    # airfoil_tip.LEO

    # =========================
    # Blade 3D
    # =========================
    "geo_3d_FA",       # blade_3d.FA
    "geo_3d_S",        # blade_3d.S
    "geo_3d_Wave_0",   # blade_3d.Wave[0]
    "geo_3d_Wave_1",   # blade_3d.Wave[1]
    "geo_3d_Rise",     # blade_3d.Rise
    "geo_3d_U_Bump_0", # blade_3d.U_Bump[0]
    "geo_3d_U_Bump_1", # blade_3d.U_Bump[1]
    "geo_3d_U_Bump_2", # blade_3d.U_Bump[2]
    "geo_3d_L_Bump_0", # blade_3d.L_Bump[0]
    "geo_3d_L_Bump_1", # blade_3d.L_Bump[1]
    "geo_3d_L_Bump_2", # blade_3d.L_Bump[2]
]

# 3. Target Label Definition (10-point PQ curve)
# Adjust to 10 points, generating P1, Q1 ... P10, Q10 for a total of 20 values
TARGET_LABELS = [f"P{i}" for i in range(1, 11)] + [f"Q{i}" for i in range(1, 11)]

# 4. Model Hyperparameters
INPUT_DIM = len(FEATURE_ORDER)   # Should be 33
OUTPUT_DIM = len(TARGET_LABELS)  # Should be 20 (P1-Q10)
HIDDEN_UNITS = 128
RANDOM_STATE = 42

# 5. Physical Units Definition (Units)

UNITS = {
    "pressure": "mmAq",
    "flow": "CFM",
    "speed": "RPM"
}
