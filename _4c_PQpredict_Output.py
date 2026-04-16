"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4c_PQpredict_Output.py
DESCRIPTION: 
    - Post-processing and export logic for prediction results.
    - Consistency: Follows GUI logic [P1..P10, Q1..Q10] without sorting.
================================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime

class PQOutputManager:
    """
    Manages data reporting, CSV exportation, and static image saving.
    """
    
    def __init__(self, output_dir="output_results"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_to_csv(self, data_dict, filename_prefix="PQ_Result"):
        """
        Saves prediction results to a CSV file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{filename_prefix}_{timestamp}.csv"
        full_path = os.path.join(self.output_dir, file_name)
        
        df = pd.DataFrame(data_dict)
        df.to_csv(full_path, index=False)
        print(f"[INFO] Data exported to: {full_path}")
        return full_path

    def plot_prediction_comparison(self, raw_data, title="PQ Curve Analysis"):
        """
        Generates and saves a PQ plot using the raw [P..Q] sequence.
        """
        data = np.array(raw_data).flatten()
        if len(data) != 20:
            print(f"[ERROR] Expected 20 values, got {len(data)}")
            return

        # Direct Mapping (No sorting)
        p_plot = data[:10]
        q_plot = data[10:]

        plt.figure(figsize=(8, 6))
        plt.plot(q_plot, p_plot, 'o-', color='red', label='AI Prediction', linewidth=2)
        
        plt.title(title, fontweight='bold')
        plt.xlabel('Flow Rate Q (CFM)', fontweight='bold')
        plt.ylabel('Static Pressure P (mmAq)', fontweight='bold')
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        
        # Save plot
        plot_path = os.path.join(self.output_dir, "latest_pq_curve.png")
        plt.savefig(plot_path)
        plt.close() # Close to prevent memory accumulation
        print(f"[INFO] PQ Curve visualization saved to: {plot_path}")

    def print_performance_metrics(self, metrics):
        """
        Prints metrics to console.
        """
        print("\n" + "*"*40)
        print("      SYSTEM PERFORMANCE REPORT")
        print("*"*40)
        for key, val in metrics.items():
            print(f" -> {key:<15} : {val:.6f}")
        print("*"*40 + "\n")

if __name__ == "__main__":
    # Test case: 10 Pressure points (high to low), 10 Flow points (low to high)
    test_p = [15.0, 14.2, 13.0, 11.5, 9.8, 8.0, 6.2, 4.5, 2.8, 1.0]
    test_q = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
    
    test_raw = test_p + test_q
    
    manager = PQOutputManager()
    manager.plot_prediction_comparison(test_raw)