"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4b_PQpredict_main.py
PURPOSE: Execution logic for PQ curve prediction using trained ResNet model.
================================================================================
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
    # 1. Path preparation
    full_json_path = path_config.get_fan_json_path(json_id) if not os.path.exists(json_id) else json_id

    # 2. Load assets
    scaler = joblib.load(path_config.SCALER_PATH)
    model = FanResNet(input_dim=algo_config.INPUT_DIM, output_dim=algo_config.OUTPUT_DIM)
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    model.eval()

    # 3. Load and parse JSON data
    with open(full_json_path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    data_map = {}
    prefix_map = {'basic': 'base', 'airfoil_root': 'root', 'airfoil_tip': 'tip', 'blade_3d': '3d'}

    for b_key, b_prefix in prefix_map.items():
        for k, v in geo.get(b_key, {}).items():
            # Handle list values (e.g., Wave, U_Bump, L_Bump)
            if isinstance(v, list):
                for i, val in enumerate(v):
                    data_map[f"geo_{b_prefix}_{k}_{i}"] = float(val)
            # Handle numeric values
            elif isinstance(v, (int, float)):
                data_map[f"geo_{b_prefix}_{k}"] = float(v)
    
    # 4. Set operating condition (Synced with algo_config.UI_FEATURE_LABELS)
    data_map['cond_operating_rpm'] = float(rpm)
    
    # 5. Feature extraction and scaling
    features = [data_map.get(lbl, 0.0) for lbl in algo_config.UI_FEATURE_LABELS]
    x_scaled = scaler.transform(np.array(features).reshape(1, -1))
    
    # Convert to Tensor [Batch, Channel, Length] for CNN
    x_tensor = torch.FloatTensor(x_scaled).unsqueeze(1) 

    # 6. Model Inference
    with torch.no_grad():
        pred_raw = model(x_tensor).numpy().flatten()

    # 7. Split P and Q values (Based on P1, Q1, P2, Q2... sequence)
    # pred_raw[0::2] -> P1, P2... (Pressure)
    # pred_raw[1::2] -> Q1, Q2... (Flow)
    return pred_raw[1::2].tolist(), pred_raw[0::2].tolist()