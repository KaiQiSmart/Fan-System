"""
============================================================
MODULE: _4b_PQpredict_main.py
DESCRIPTION: 
    - AI Inference Engine for PQ Curve Prediction.
    - FIXED: Explicitly maps 33 features by index to prevent data misalignment.
    - Synchronized with _3b training logic.
============================================================
"""
import os
import torch
import joblib
import json
import numpy as np
import glob
import _4a_PQpredict_path as path_config
import _4a_PQpredict_algo_params as algo_config
from _3b_PQmodel_train import FanResNet 

def predict_logic(json_id, rpm, model_path):
    """
    json_id: Fan JSON filename or path.
    rpm: Target speed (RPM).
    model_path: Absolute path to the .pth weights file.
    """
    try:

        full_json_path = path_config.get_fan_json_path(json_id) if not os.path.exists(json_id) else json_id
        model_folder = os.path.dirname(model_path)
        scaler_files = glob.glob(os.path.join(model_folder, "*.joblib"))
        if not scaler_files:
            raise FileNotFoundError(f"Missing .joblib in {model_folder}")
        
        scaler = joblib.load(scaler_files[0])

        model = FanResNet(input_dim=algo_config.INPUT_DIM, output_dim=algo_config.OUTPUT_DIM)
        model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
        model.eval()

        with open(full_json_path, 'r', encoding='utf-8') as f:
            geo = json.load(f)
        
        dm = {} # Data Map

        # [A] Basic Geometry (Index 0-6)
        b = geo.get("basic", {})
        dm["geo_base_FW"] = float(b.get("FW", 0))
        dm["geo_base_FH"] = float(b.get("FH", 0))
        dm["geo_base_OD"] = float(b.get("OD", 0))
        dm["geo_base_ID"] = float(b.get("ID", 0))
        dm["geo_base_HH"] = float(b.get("HH", 0))
        dm["geo_base_BC"] = float(b.get("BC", 0))
        dm["geo_base_CG"] = float(b.get("CG", 0))

        # [B] Operating Condition (Index 7) 
        dm["cond_operating_rpm"] = float(rpm)

        # [C] Airfoil Root (Index 8-14)
        r = geo.get("airfoil_root", {})
        for k in ["CH", "CAM", "CP", "TM", "TTE", "IA", "LEO"]:
            dm[f"geo_root_{k}"] = float(r.get(k, 0))

        # [D] Airfoil Tip (Index 15-21)
        t = geo.get("airfoil_tip", {})
        for k in ["CH", "CAM", "CP", "TM", "TTE", "IA", "LEO"]:
            dm[f"geo_tip_{k}"] = float(t.get(k, 0))

        # [E] Blade 3D (Index 22-32)
        d3 = geo.get("blade_3d", {})
        dm["geo_3d_FA"] = float(d3.get("FA", 0))
        dm["geo_3d_S"]  = float(d3.get("S", 0))
        
  
        waves = d3.get("Wave", [0.0, 0.0])
        dm["geo_3d_Wave_0"], dm["geo_3d_Wave_1"] = float(waves[0]), float(waves[1])
        
        dm["geo_3d_Rise"] = float(d3.get("Rise", 0))

        ub = d3.get("U_Bump", [0.0, 0.0, 0.0])
        dm["geo_3d_U_Bump_0"], dm["geo_3d_U_Bump_1"], dm["geo_3d_U_Bump_2"] = float(ub[0]), float(ub[1]), float(ub[2])
        
        lb = d3.get("L_Bump", [0.0, 0.0, 0.0])
        dm["geo_3d_L_Bump_0"], dm["geo_3d_L_Bump_1"], dm["geo_3d_L_Bump_2"] = float(lb[0]), float(lb[1]), float(lb[2])

  
        features = []
        for lbl in algo_config.UI_FEATURE_LABELS:
            val = dm.get(lbl, 0.0)
            features.append(val)

        # print(f"DEBUG: Scaler Input (33 values) = {features}")
        # ------------------------------------

  
        x_scaled = scaler.transform(np.array(features).reshape(1, -1))
        x_tensor = torch.FloatTensor(x_scaled).unsqueeze(1) # ResNet: [1, 1, 33]

        with torch.no_grad():
            pred_raw = model(x_tensor).numpy().flatten()

        return pred_raw.tolist()

    except Exception as e:
        print(f"[ERROR] predict_logic error: {e}")
        raise e