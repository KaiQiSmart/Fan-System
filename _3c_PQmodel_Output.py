"""
================================================================================
MODULE: _3c_PQmodel_Output.py
DESCRIPTION: 
Unified output interface for the Fan Integrated Design Platform.
Saves model weights (.pth), scaler (.joblib), and config (.json) into MODEL_DIR.
================================================================================
"""
import torch
import joblib
import os
import json
from _3a_PQmodel_path import MODEL_DIR

def export_standalone(model, scaler, feature_names, model_name="A40", version="00"):
    """
    Execute the standalone saving logic.
    
    Args:
        model: Trained ResNet model instance.
        scaler: sklearn StandardScaler/MinMaxScaler instance.
        feature_names (list): List of input feature names for the model.
        model_name (str): The fan model series (e.g., 'A40', 'A50').
        version (str): The version iteration (e.g., '00', '01').
    """
    try:
        # Step 1: Ensure the centralized MODEL_DIR exists
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Step 2: Define the naming convention
        # Format: {model_name}_{version}_{type}.extension
        file_prefix = f"{model_name}_{version}"
        
        weights_path = os.path.join(MODEL_DIR, f"{file_prefix}_weights.pth")
        scaler_path  = os.path.join(MODEL_DIR, f"{file_prefix}_scaler.joblib")
        config_path  = os.path.join(MODEL_DIR, f"{file_prefix}_model.json")
        
        # Step 3: Save Model Weights (The 'Brain')
        # Use CPU mapped storage for better cross-platform compatibility if needed
        torch.save(model.state_dict(), weights_path)
        
        # Step 4: Save Scaler (The 'Filter' to prevent NaN during inference)
        joblib.dump(scaler, scaler_path)
        
        # Step 5: Save Model Configuration (The 'Manual')
        input_dim = len(feature_names)
        config_data = {
            "model_metadata": {
                "model_name": model_name,
                "version": version,
                "architecture": "ResNet"
            },
            "input_config": {
                "input_dim": input_dim,
                "feature_names": feature_names
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
            
        # Success Output
        print("\n" + "="*60)
        print(f"[SUCCESS] Model Exported to: {MODEL_DIR}")
        print(f"1. Weights: {os.path.basename(weights_path)}")
        print(f"2. Scaler:  {os.path.basename(scaler_path)}")
        print(f"3. Config:  {os.path.basename(config_path)}")
        print("="*60 + "\n")
        
        return True

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to save output files: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage for testing
    print("Testing output module...")
    # export_standalone(my_model, my_scaler, ['RPM', 'Blade_Count', ...], "A40", "01")