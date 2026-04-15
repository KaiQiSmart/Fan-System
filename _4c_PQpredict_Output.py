"""
================================================================================
PROJECT: PQ Prediction System
MODULE: _4c_PQpredict_Output.py
DESCRIPTION: 
    This module handles the post-processing of prediction results. 
    It provides functionalities for:
    1. Generating performance metric reports (MSE, MAE, R2).
    2. Visualizing actual vs. predicted data using Matplotlib.
    3. Exporting processed results to CSV files for external analysis.
USAGE:
    Import the PQOutputManager class into the main execution script 
    (_4b_PQpredict_main.py) or the GUI module (_4_PQpredict_GUI.py).
================================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class PQOutputManager:
    """
    Manages data visualization, console reporting, and file exportation.
    """
    
    def __init__(self, output_dir="output_results"):
        """
        Initializes the output directory for storing plots and CSV files.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_to_csv(self, data_dict, filename_prefix="PQ_Result"):
        """
        Converts result dictionary to a DataFrame and saves it as a CSV.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{filename_prefix}_{timestamp}.csv"
        full_path = os.path.join(self.output_dir, file_name)
        
        df = pd.DataFrame(data_dict)
        df.to_csv(full_path, index=False)
        print(f"[INFO] Data exported to: {full_path}")
        return full_path

    def plot_prediction_comparison(self, actual, predicted, title="PQ Prediction Analysis"):
        """
        Creates and saves a comparison plot between actual and predicted values.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(actual, label='Actual', color='blue', linewidth=1.5)
        plt.plot(predicted, label='Predicted', color='red', linestyle='--', linewidth=1.5)
        
        plt.title(title)
        plt.xlabel('Sample Index')
        plt.ylabel('PQ Value')
        plt.legend(loc='upper right')
        plt.grid(True, linestyle=':', alpha=0.7)
        
        # Save plot to file
        plot_path = os.path.join(self.output_dir, "latest_prediction_plot.png")
        plt.savefig(plot_path)
        plt.show()
        print(f"[INFO] Visualization saved to: {plot_path}")

    def print_performance_metrics(self, metrics):
        """
        Formats and prints model metrics to the standard output.
        """
        print("\n" + "*"*40)
        print("       SYSTEM PERFORMANCE REPORT")
        print("*"*40)
        for key, val in metrics.items():
            print(f" -> {key:<15} : {val:.6f}")
        print("*"*40 + "\n")

if __name__ == "__main__":
    # --- Integration Test Case ---
    # Simulated data for standalone execution check
    test_actual = [1.0, 1.2, 1.5, 1.3, 1.1]
    test_predict = [1.05, 1.18, 1.45, 1.32, 1.08]
    test_metrics = {
        "Mean Squared Error": 0.0024,
        "R-Squared": 0.9850
    }
    
    output_service = PQOutputManager()
    output_service.print_performance_metrics(test_metrics)
    output_service.plot_prediction_comparison(test_actual, test_predict)
    
    test_results = {
        "Actual_Value": test_actual,
        "Predicted_Value": test_predict
    }
    output_service.export_to_csv(test_results)