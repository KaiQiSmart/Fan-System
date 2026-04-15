# _6a_Database_path.py
import os

class DatabasePath:
    def __init__(self):
        # Base directory where the script is located
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Path for Blade Parameters (Input)
        self.fan_data_dir = os.path.normpath(os.path.join(self.root_dir, "1_Input", "1_Blade_Parameters"))
        
        # 2. Path for PQ Prediction Results (Output)
        self.output_dir = os.path.normpath(os.path.join(self.root_dir, "2_Output", "3_PQPredict"))

        # Ensure directories exist to avoid FileNotFoundError
        for p in [self.fan_data_dir, self.output_dir]:
            if not os.path.exists(p):
                print(f"Warning: Directory not found: {p}")

    def get_blade_files(self):
        """List all JSON files in the Blade_Parameters folder."""
        if not os.path.exists(self.fan_data_dir): return []
        return [f for f in os.listdir(self.fan_data_dir) if f.endswith('.json')]

    def get_pq_file_path(self, model_id):
        """Find the corresponding PQ prediction file in Output directory."""
        # Assuming PQ files are named as {model_id}_PQ.json or similar
        return os.path.join(self.output_dir, f"{model_id}_PQ.json")