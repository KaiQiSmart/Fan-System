"""
============================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4b_PQpredict_main.py
============================================================
"""
import os
import torch
import joblib
import json
import numpy as np
import _4a_PQpredict_path as path_config
import _4a_PQpredict_algo_params as algo_config
from _3b_PQmodel_train import FanResNet 

def predict_logic(json_id, rpm, model_path):

    full_json_path = path_config.get_fan_json_path(json_id) if not os.path.exists(json_id) else json_id


    scaler = joblib.load(path_config.SCALER_PATH)
    model = FanResNet(input_dim=algo_config.INPUT_DIM, output_dim=algo_config.OUTPUT_DIM)
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    model.eval()

    with open(full_json_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    data_map = {}

    prefix_map = {'basic': 'base', 'airfoil_root': 'root', 'airfoil_tip': 'tip', 'blade_3d': '3d'}
    for b_key, b_prefix in prefix_map.items():
        for k, v in geo.get(b_key, {}).items():
            if isinstance(v, (int, float)):
                data_map[f"geo_{b_prefix}_{k}"] = float(v)
    
  
    data_map['test_rpm'] = float(rpm)
    

    features = [data_map.get(lbl, 0.0) for lbl in algo_config.UI_FEATURE_LABELS]
    x_scaled = scaler.transform(np.array(features).reshape(1, -1))
    x_tensor = torch.FloatTensor(x_scaled).unsqueeze(1) 

    with torch.no_grad():
        pred_raw = model(x_tensor).numpy().flatten()

    return pred_raw[1::2].tolist(), pred_raw[0::2].tolist() 