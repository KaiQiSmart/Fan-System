"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4_PQpredict_GUI.py
DESCRIPTION: 
    - Auto-detection: Automatically selects the AI model category based on FW value.
    - User Interface: Clean display of Fan Names and Model IDs (e.g., A40_00).
    - Multi-tasking: Allows queuing multiple fans for PQ curve comparison.
================================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import numpy as np
import json

import _4a_PQpredict_path as path_config
from _4b_PQpredict_main import predict_logic

class PQPredictGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.parent = parent
        self.prediction_tasks = []
        self.active_model_files = {"pth": None}
        
        # Mapping for manual or auto selection
        self.model_mapping = {
            "0_All": path_config.PATH_MODEL_ALL,
            "1_under50": path_config.PATH_MODEL_UNDER50,
            "2_50 to 69": path_config.PATH_MODEL_50_TO_69,
            "3_over70": path_config.PATH_MODEL_OVER70
        }
        
        self._build_widgets()

    def _build_widgets(self):
        """Initialize the main GUI layout."""
        self.main_container = tk.Frame(self, bg="#f5f5f5")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- LEFT PANEL: Configuration and Queue ---
        self.left_panel = tk.Frame(self.main_container, width=420, bg="#f5f5f5")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)

        tk.Label(self.left_panel, text="AI PQ Predictor", font=("Arial", 16, "bold"), 
                 bg="#f5f5f5", fg="#2c3e50").pack(pady=(5, 10))

        # 1. Setup Task Section
        config_frame = tk.LabelFrame(self.left_panel, text=" 1. Setup Task ", padx=15, pady=10, 
                                     bg="white", font=("Arial", 10, "bold"))
        config_frame.pack(fill="x", pady=5)

        # Fan Geometry Selection
        tk.Label(config_frame, text="Fan Geometry:", bg="white").pack(anchor="w")
        self.display_json_name = tk.StringVar(value="No File Selected")
        self.full_json_path = "" 
        
        json_row = tk.Frame(config_frame, bg="white")
        json_row.pack(fill="x", pady=(0, 5))
        tk.Entry(json_row, textvariable=self.display_json_name, state="readonly", 
                 relief="solid", bd=1, readonlybackground="#fdfdfd").pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(json_row, text="Select", command=self.browse_json).pack(side="right")

        # Target RPM Input
        tk.Label(config_frame, text="Target RPM:", bg="white").pack(anchor="w")
        self.rpm_entry = tk.Entry(config_frame, relief="solid", bd=1, justify="center")
        self.rpm_entry.insert(0, "4000")
        self.rpm_entry.pack(fill="x", pady=(5, 10))

        # AI Model ID Display (Detected automatically)
        tk.Label(config_frame, text="AI Model (Detected):", bg="white").pack(anchor="w")
        self.display_model_id = tk.StringVar(value="None")
        tk.Entry(config_frame, textvariable=self.display_model_id, state="readonly", 
                 relief="flat", readonlybackground="#f0f0f0").pack(fill="x", pady=(0, 5))
        
        # Category Dropdown (Updated via auto-detect)
        self.model_cat_var = tk.StringVar()
        self.model_combo = ttk.Combobox(config_frame, textvariable=self.model_cat_var, state="readonly")
        self.model_combo['values'] = list(self.model_mapping.keys())
        self.model_combo.pack(fill="x", pady=(5, 10))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Add to Queue Button
        tk.Button(config_frame, text="ADD TO QUEUE", command=self.add_task, 
                  bg="#107c10", fg="white", font=("Arial", 9, "bold")).pack(fill="x", pady=(10, 0))

        # 2. Comparison Queue Table
        tk.Label(self.left_panel, text="Comparison Queue:", font=("Arial", 10, "bold"), bg="#f5f5f5").pack(anchor="w", pady=(15, 0))
        tree_frame = tk.Frame(self.left_panel, bg="white", bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Fan", "RPM", "Model"), show='headings')
        self.tree.heading("Fan", text="Fan Name")
        self.tree.heading("RPM", text="RPM")
        self.tree.heading("Model", text="AI Model")
        self.tree.column("Fan", width=140); self.tree.column("RPM", width=60, anchor="center"); self.tree.column("Model", width=120)
        self.tree.pack(side="left", fill="both", expand=True)
        
        tk.Button(self.left_panel, text="Clear Queue", command=self.clear_tasks, bg="#d83b01", fg="white").pack(fill="x", pady=5)

        # Global Action Button
        self.predict_btn = tk.Button(self.left_panel, text="START PREDICTION", bg="#0078d4", fg="white", 
                                     font=("Arial", 12, "bold"), height=2, command=self.run_prediction)
        self.predict_btn.pack(fill="x", pady=(10, 0))

        # --- RIGHT PANEL: Visualization ---
        self.right_panel = tk.Frame(self.main_container, bg="white", bd=1, relief="solid")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.toolbar_frame = tk.Frame(self.right_panel, bg="white")
        self.toolbar_frame.pack(side="top", fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def on_model_change(self, event=None):
        """Handles manual model category changes or triggered updates."""
        selected_key = self.model_cat_var.get()
        folder_path = self.model_mapping.get(selected_key)
        
        if folder_path:
            # Retrieve model files from the target directory
            files = path_config.get_model_files_from_folder(folder_path)
            self.active_model_files["pth"] = files.get("weights_pth")
            
            # Update the UI display with the clean model ID
            raw_name = os.path.basename(files.get("weights_pth", "None"))
            clean_id = raw_name.replace("_weights.pth", "").replace(".pth", "")
            self.display_model_id.set(clean_id)

    def browse_json(self):
        """Opens file dialog and triggers the auto-detection logic."""
        path = filedialog.askopenfilename(initialdir=path_config.FAN_DATA_DIR, 
                                          filetypes=(("JSON files", "*.json"),))
        if path:
            self.full_json_path = path
            self.display_json_name.set(os.path.basename(path).replace(".json", ""))
            # Trigger logic to detect FW and update model selection
            self._background_auto_detect(path)

    def _background_auto_detect(self, json_path):
        """Parses the JSON file to detect FW and set the appropriate model category."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                fw_val = 0.0
                if "basic" in data and isinstance(data["basic"], dict):
                    # Access data['basic']['FW']
                    fw_val = float(data["basic"].get("FW", 0))
                else:
                    # Fallback to top-level search if 'basic' is missing
                    fw_val = float(data.get("FW", 0))
            
            # Logic for selecting category based on FW
            if fw_val < 50:
                target_category = "1_under50"
            elif 50 <= fw_val <= 69:
                target_category = "2_50 to 69"
            else:
                target_category = "3_over70"
            
            # Programmatically set the combobox and trigger path updates
            self.model_cat_var.set(target_category)
            self.on_model_change()

        except Exception as e:
            print(f"Auto-detect Error: {e}")
            self.display_model_id.set("Detection Failed")

    def add_task(self):
        """Validates inputs and adds the current configuration to the task queue."""
        if not self.full_json_path or not self.active_model_files["pth"]:
            messagebox.showwarning("Warning", "Please select a Fan Geometry first.")
            return

        task = {
            "json_filename": os.path.basename(self.full_json_path),
            "fan_name": self.display_json_name.get(),
            "rpm": self.rpm_entry.get().strip(),
            "weights_path": self.active_model_files["pth"],
            "model_id": self.display_model_id.get()
        }
        self.prediction_tasks.append(task)
        self.tree.insert("", tk.END, values=(task["fan_name"], task["rpm"], task["model_id"]))

    def clear_tasks(self):
        """Resets the comparison queue."""
        self.prediction_tasks = []
        for item in self.tree.get_children():
            self.tree.delete(item)

    def run_prediction(self):
        """Executes the prediction logic for all tasks in the queue and plots results."""
        if not self.prediction_tasks:
            messagebox.showinfo("Queue Empty", "Please add tasks to the queue first.")
            return

        self.ax.clear()
        success_count = 0

        for task in self.prediction_tasks:
            try:
                # Call logic from external module
                raw_output = predict_logic(task["json_filename"], task["rpm"], task["weights_path"])
                data = np.array(raw_output).flatten()

                # Expecting 10 pairs (Pressure, Flow Rate)
                if len(data) == 20:
                    self.ax.plot(data[10:], data[:10], marker='o', markersize=4, 
                                 label=f"{task['fan_name']} ({task['rpm']} RPM)")
                    success_count += 1
            except Exception as e:
                print(f"Execution Error for {task['fan_name']}: {e}")

        if success_count > 0:
            self.ax.set_title("AI Predicted PQ Performance", fontweight='bold')
            self.ax.set_xlabel("Airflow Q (CFM)")
            self.ax.set_ylabel("Static Pressure P (mmAq)")
            self.ax.legend(loc='best', fontsize=8)
            self.ax.grid(True, linestyle=':')
            self.ax.set_xlim(left=0)
            self.ax.set_ylim(bottom=0)
        else:
            messagebox.showerror("Error", "All predictions failed. Check pathing or data format.")
        
        self.canvas.draw()

if __name__ == "__main__":
    # Application Entry Point
    root = tk.Tk()
    root.title("Fan Integrated Design Platform - AI Hub")
    root.geometry("1200x850")
    
    app = PQPredictGUI(root)
    app.pack(fill="both", expand=True)
    
    root.mainloop()