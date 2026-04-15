"""
============================================================
MODULE: _4a_PQpredict_algo_params.py
============================================================
"""

UI_FEATURE_LABELS = [
    # Basic
    "geo_base_FW", "geo_base_FH", "geo_base_OD", "geo_base_ID", 
    "geo_base_HH", "geo_base_BC", "geo_base_CG",

    # Operating Condition
    "cond_operating_rpm",

    # Airfoil Root
    "geo_root_CH", "geo_root_CAM", "geo_root_CP", "geo_root_TM", 
    "geo_root_TTE", "geo_root_IA", "geo_root_LEO",

    # Airfoil Tip
    "geo_tip_CH", "geo_tip_CAM", "geo_tip_CP", "geo_tip_TM", 
    "geo_tip_TTE", "geo_tip_IA", "geo_tip_LEO",

    # Blade 3D
    "geo_3d_FA", "geo_3d_S", "geo_3d_Wave_0", "geo_3d_Wave_1", 
    "geo_3d_Rise", "geo_3d_U_Bump_0", "geo_3d_U_Bump_1", "geo_3d_U_Bump_2", 
    "geo_3d_L_Bump_0", "geo_3d_L_Bump_1", "geo_3d_L_Bump_2"
]

INPUT_DIM = len(UI_FEATURE_LABELS)  # 33
OUTPUT_DIM = 20

TARGET_LABELS = [f"{pq}{i}" for i in range(1, 11) for pq in ['P', 'Q']]

RANDOM_STATE = 42
UNITS = {
    "pressure": "mmAq",
    "flow": "CFM",
    "speed": "RPM"
}