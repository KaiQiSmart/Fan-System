"""
============================================================
PROJECT: Fan Integrated Design Platform
MODULE: _4_PQpredict_GUI.py
DESCRIPTION: 
    PQ performance prediction GUI.
Fix: Restored the dependency on algo_params.UNITS.
Fix: Ensured proper initialization of the rpm_entry widget to resolve the AttributeError.
Fix: Ensured compatibility with the Frame structure embedded in _0_GUI.py.
============================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

import _4a_PQpredict_path as path_config
import _4a_PQpredict_algo_params as algo_config
from _4b_PQpredict_main import predict_logic

class PQPredictGUI:
    def __init__(self, container):
        
        self.container = container
        
    
        if hasattr(self.container, 'title') and isinstance(self.container, tk.Tk):
            self.container.title("Fan PQ Performance Prediction")
        
        
        self.prediction_cases = []
        
       
        self.setup_ui()
        self.refresh_model_list()

    def setup_ui(self):
        
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        
        self.left_panel = tk.Frame(self.main_frame, width=320, padx=10, pady=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.left_panel, text="PQ Curve Prediction", font=("Arial", 14, "bold")).pack(pady=10)

        
        model_frame = tk.LabelFrame(self.left_panel, text="1. Select AI Model", padx=5, pady=5)
        model_frame.pack(fill=tk.X, pady=5)

        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly")
        self.model_combo.pack(fill=tk.X, pady=5)
        tk.Button(model_frame, text="Refresh Model List", command=self.refresh_model_list).pack(fill=tk.X)

        
        input_frame = tk.LabelFrame(self.left_panel, text="2. Prediction Settings", padx=5, pady=5)
        input_frame.pack(fill=tk.X, pady=5)

        
        tk.Label(input_frame, text=f"Target Speed ({algo_config.UNITS['speed']}):").pack(anchor="w")
        self.rpm_entry = tk.Entry(input_frame)
        self.rpm_entry.insert(0, "4000") 
        self.rpm_entry.pack(fill=tk.X, pady=5)

        tk.Button(input_frame, text="Select Blade JSON", command=self.add_case, bg="#E1E1E1").pack(fill=tk.X, pady=5)

        
        tk.Label(self.left_panel, text="Case List:").pack(anchor="w", pady=(10, 0))
        self.tree = ttk.Treeview(self.left_panel, columns=("File", "RPM"), show='headings', height=8)
        self.tree.heading("File", text="File")
        self.tree.heading("RPM", text="RPM")
        self.tree.column("File", width=160)
        self.tree.column("RPM", width=70)
        self.tree.pack(fill=tk.BOTH, expand=True)

        
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_selected).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Clear All", command=self.clear_cases).pack(side=tk.LEFT, expand=True, fill=tk.X)

        
        self.predict_btn = tk.Button(self.left_panel, text="START PREDICTION", bg="#2196F3", fg="white", 
                                     font=("Arial", 12, "bold"), height=2, command=self.run_prediction)
        self.predict_btn.pack(fill=tk.X, pady=10)

        
        self.right_panel = tk.Frame(self.main_frame, bg="white")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_model_list(self):
        """Refresh the model list"""
        if os.path.exists(path_config.MODEL_DIR):
            models = [f for f in os.listdir(path_config.MODEL_DIR) if f.endswith('.pth')]
            self.model_combo['values'] = models
            if models: self.model_combo.current(0)

    def add_case(self):
        """Select JSON and add to the list"""
        file_path = filedialog.askopenfilename(
            initialdir=path_config.FAN_DATA_DIR,
            title="Select Blade Geometry JSON",
            filetypes=(("JSON files", "*.json"), ("all files", "*.*"))
        )
        if file_path:
            json_name = os.path.basename(file_path)
            rpm = self.rpm_entry.get() 
            self.prediction_cases.append((json_name, rpm))
            self.tree.insert("", tk.END, values=(json_name, rpm))

    def remove_selected(self):
        selected = self.tree.selection()
        for item in selected:
            idx = self.tree.index(item)
            del self.prediction_cases[idx]
            self.tree.delete(item)

    def clear_cases(self):
        self.prediction_cases.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.ax.clear()
        self.canvas.draw()

    def run_prediction(self):
        if not self.prediction_cases:
            messagebox.showwarning("Warning", "Please add at least one case!")
            return
        
        model_file = self.model_var.get()
        if not model_file:
            messagebox.showwarning("Warning", "Please select a model!")
            return

        model_path = path_config.get_model_path(model_file)
        self.ax.clear()

        for json_id, rpm in self.prediction_cases:
            try:
                q_list, p_list = predict_logic(json_id, rpm, model_path)
                
                label_name = f"{json_id} ({rpm} RPM)"
                self.ax.plot(q_list, p_list, marker='o', linestyle='-', label=label_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed for {json_id}: {str(e)}")
                continue

        self.ax.set_title("Predicted Fan PQ Curves", fontsize=12, fontweight='bold')
        self.ax.set_xlabel(f"Flow Rate ({algo_config.UNITS['flow']})")
        self.ax.set_ylabel(f"Static Pressure ({algo_config.UNITS['pressure']})")
        self.ax.legend()
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    app = PQPredictGUI(root)
    root.mainloop()