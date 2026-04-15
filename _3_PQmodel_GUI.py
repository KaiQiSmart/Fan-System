"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _3_PQmodel_GUI.py
DESCRIPTION: 
    - Training Interface: Handles parameter input, training progress display, 
      and result validation.
    - Logic Separation: Training triggers _3b, manual export triggers _3c.
    - Dimension Alignment: Ensures FEATURE_ORDER is correctly passed to 
      prevent 1024/1408 dimension conflicts.
================================================================================
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.metrics import mean_absolute_error

# Import configuration and paths
from _3a_PQmodel_path import PQ_DATA_DIR, MODEL_DIR
import _3a_PQmodel_algo_params as algo_params

# Import logic modules
import _3b_PQmodel_train as trainer
import _3c_PQmodel_Output as exporter

class ModelTrainingGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.parent = parent
        
        # Internal State Management (Trained objects are cached here, not auto-saved)
        self.pq_source_dir = PQ_DATA_DIR
        self.trained_results = None  
        self.current_sample_idx = 0

        self._build_widgets()

    def _build_widgets(self):
        # --- 1. System Paths Panel ---
        path_frame = tk.LabelFrame(self, text=" System Paths ", padx=15, pady=10, bg="white", font=("Arial", 10, "bold"))
        path_frame.pack(side="top", fill="x", padx=20, pady=5)

        tk.Label(path_frame, text="PQ Source:", bg="white").grid(row=0, column=0, sticky="w")
        self.lbl_source = tk.Label(path_frame, text=self.pq_source_dir, fg="#2c3e50", bg="white", font=("Consolas", 9))
        self.lbl_source.grid(row=0, column=1, padx=10, sticky="w")
        tk.Button(path_frame, text="Browse", command=self.browse_source).grid(row=0, column=2)

        # --- 2. Training Control Panel (Grid Layout) ---
        config_frame = tk.LabelFrame(self, text=" Training Control ", padx=15, pady=10, bg="white", font=("Arial", 10, "bold"))
        config_frame.pack(side="top", fill="x", padx=20, pady=5)
        
        # Row 1: Split Settings
        tk.Label(config_frame, text="Split (Tr/Val/Te %):", bg="white").grid(row=0, column=0, sticky="w")
        entry_style = {"width": 6, "relief": "solid", "bd": 1, "justify": "center"}
        self.ent_tr = tk.Entry(config_frame, **entry_style); self.ent_tr.insert(0, str(algo_params.TRAIN_RATIO))
        self.ent_va = tk.Entry(config_frame, **entry_style); self.ent_va.insert(0, str(algo_params.VAL_RATIO))
        self.ent_te = tk.Entry(config_frame, **entry_style); self.ent_te.insert(0, str(algo_params.TEST_RATIO))
        self.ent_tr.grid(row=0, column=1, padx=2)
        self.ent_va.grid(row=0, column=2, padx=2)
        self.ent_te.grid(row=0, column=3, padx=2)

        # Row 2: Epochs 
        tk.Label(config_frame, text="Total Epochs:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        self.ent_epochs = tk.Entry(config_frame, width=10, relief="solid", bd=1, justify="center")
        self.ent_epochs.insert(0, str(algo_params.DEFAULT_EPOCHS))
        self.ent_epochs.grid(row=1, column=1, columnspan=2, sticky="w", padx=2)

        # Function Buttons
        self.btn_train = tk.Button(config_frame, text="🚀 START TRAINING", command=self.on_start_training, 
                                 bg="#0078d4", fg="white", font=("Arial", 9, "bold"), padx=20)
        self.btn_train.grid(row=0, column=4, rowspan=2, padx=20)
        
        self.btn_save = tk.Button(config_frame, text="💾 EXPORT MODEL", command=self.on_export_model, 
                                 bg="#107c10", fg="white", font=("Arial", 9, "bold"), state="disabled", padx=20)
        self.btn_save.grid(row=0, column=5, rowspan=2)

        # --- 3. Sample Review Navigation Bar ---
        self.review_frame = tk.Frame(self, bg="#e0e0e0", pady=5)
        self.review_frame.pack(side="top", fill="x", padx=20, pady=5)
        
        self.btn_prev = tk.Button(self.review_frame, text="◀ PREV", command=self.prev_sample, state="disabled")
        self.btn_prev.pack(side="left", padx=20)
        self.lbl_info = tk.Label(self.review_frame, text="READY TO TRAIN", bg="#e0e0e0", font=("Segoe UI", 10, "bold"))
        self.lbl_info.pack(side="left", expand=True)
        self.btn_next = tk.Button(self.review_frame, text="NEXT ▶", command=self.next_sample, state="disabled")
        self.btn_next.pack(side="left", padx=20)

        # --- 4. Display Area (Plot + Log) ---
        display_frame = tk.Frame(self, bg="#f5f5f5")
        display_frame.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        plot_container = tk.Frame(display_frame, bg="white", bd=1, relief="solid")
        plot_container.pack(side="left", fill="both", expand=True)
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        console_container = tk.Frame(display_frame, bg="#f0f0f0", bd=1, relief="solid")
        console_container.pack(side="right", fill="y", padx=(15, 0))
        self.log_area = scrolledtext.ScrolledText(console_container, width=55, bg="#fcfcfc", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

    # --- Functional Logic ---
    def browse_source(self):
        path = filedialog.askdirectory(initialdir=self.pq_source_dir)
        if path: self.pq_source_dir = path; self.lbl_source.config(text=path)

    def log(self, text):
        self.log_area.insert(tk.END, f" {text}\n")
        self.log_area.see(tk.END); self.update_idletasks()

    def on_start_training(self):
        """Triggers _3b for training; results are cached in memory"""
        try:
            self.log_area.delete('1.0', tk.END)
            self.log("[SYSTEM] Initializing Training...")
            
            # Get Epochs
            epochs = int(self.ent_epochs.get())
            
            # Call training module
            results = trainer.train(epochs=epochs, gui_logger=self.log)
            
            if results:
                self.trained_results = results
                self.current_sample_idx = 0
                self.btn_save.config(state="normal") # Enable manual export button
                self.btn_prev.config(state="normal")
                self.btn_next.config(state="normal")
                self.update_review_display()
                self.log("[SUCCESS] Training Finished. Objects held in memory.")
            
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            messagebox.showerror("Training Error", str(e))

    def on_export_model(self):
        """Calls _3c to execute physical file saving upon click"""
        if not self.trained_results: return

        try:
            self.log("[SYSTEM] Exporting files to disk...")
            # Extract from cached results
            model = self.trained_results['model']
            scaler = self.trained_results['scaler']
            # Feature name list (from algo_params or _3b)
            f_names = algo_params.FEATURE_ORDER 

            # Call output module to perform saving
            success = exporter.export_standalone(model, scaler, f_names)
            
            if success:
                self.log("[SUCCESS] Weights and Scaler saved successfully.")
                messagebox.showinfo("Export Success", "Model and Scaler have been updated.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save files: {e}")

    def update_review_display(self):
        """Synchronously display validation PQ curves after training"""
        res = self.trained_results
        y_true = res['test_y'][self.current_sample_idx]
        y_pred = res['test_pred'][self.current_sample_idx]
        fan_name = res['test_names'][self.current_sample_idx]
        
        # Label Order: [P1..P10, Q1..Q10]
        
        p_true = y_true[:10]
        q_true = y_true[10:]

        p_pred = y_pred[:10]
        q_pred = y_pred[10:]
        
        mae = mean_absolute_error(y_true, y_pred)
        self.lbl_info.config(text=f"Review: {self.current_sample_idx+1}/{len(res['test_y'])} | {fan_name} | MAE: {mae:.2f}")
        
        self.ax.clear()
        self.ax.plot(q_true, p_true, 'go-', label='Actual', alpha=0.6)
        self.ax.plot(q_pred, p_pred, 'rx--', label='AI Predict')
        self.ax.set_title("Validation Result (P vs Q)")
        self.ax.set_xlabel("Flow Rate (CFM)"); self.ax.set_ylabel("Static Pressure (mmAq)")
        self.ax.legend(); self.ax.grid(True, linestyle=':')
        self.canvas.draw()

    def prev_sample(self):
        if self.current_sample_idx > 0:
            self.current_sample_idx -= 1; self.update_review_display()

    def next_sample(self):
        if self.current_sample_idx < len(self.trained_results['test_y']) - 1:
            self.current_sample_idx += 1; self.update_review_display()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fan Design AI - Training Hub")
    root.geometry("1150x800")
    gui = ModelTrainingGUI(root)
    gui.pack(fill="both", expand=True)
    root.mainloop()