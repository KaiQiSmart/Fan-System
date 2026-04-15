"""
================================================================================
MODULE: _3c_PQmodel_Output.py
DESCRIPTION: 
Unified output interface: Triggered manually via the GUI to save.
Responsible for saving model weights, scaler, and dimension configurations separately.
================================================================================
"""
import torch
import joblib
import os
import json
from _3a_PQmodel_path import MODEL_DIR, SCALER_PATH, MODEL_PATH

def export_standalone(model, scaler, feature_names):
    """
    Execute the standalone saving logic.
    param model: Trained model instance
    param scaler: sklearn Scaler instance
    param feature_names: List of feature names (used to calculate input_dim)
    """
    try:
        # Ensure the directory exists
        os.makedirs(MODEL_DIR, exist_ok=True)
        
      
        torch.save(model.state_dict(), MODEL_PATH)
        
       
        joblib.dump(scaler, SCALER_PATH)
        
        input_dim = len(feature_names)
        config_path = os.path.join(MODEL_DIR, "model_config.json")
        config_data = {
            "input_dim": input_dim,
            "feature_names": feature_names
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
            
        print(f"[SUCCESS] Files saved manually to: {MODEL_DIR}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save: {str(e)}")
        return False