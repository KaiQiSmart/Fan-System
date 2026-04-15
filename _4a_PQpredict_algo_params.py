"""
============================================================
MODULE: _4a_PQpredict_algo_params.py
============================================================
"""

UI_FEATURE_LABELS = [
    "geo_base_FW", "geo_base_FH", "geo_base_OD", "geo_base_ID", 
    "geo_base_BC", "geo_base_H", "geo_base_CG",
    "geo_root_CAM", "geo_root_CP", "geo_root_TM", "geo_root_TTE", "geo_root_IA", "geo_root_LEO",
    "geo_tip_CAM", "geo_tip_CP", "geo_tip_TM", "geo_tip_TTE", "geo_tip_IA", "geo_tip_LEO",
    "geo_3d_FA", "geo_3d_S",
    "test_rpm" 
]

INPUT_DIM = 22
OUTPUT_DIM = 20


UNITS = {"pressure": "mmAq", "flow": "CFM", "speed": "RPM"}
RANDOM_STATE = 42