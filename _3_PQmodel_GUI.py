"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _3_PQmodel_GUI.py
DESCRIPTION: 
    - Enhanced Training Interface with modern styling and robust validation.
    - Logic: Sequential execution from data loading (_3b) to export (_3c).
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.metrics import mean_absolute_error
import os

# Import configuration and paths
from _3a_PQmodel_path import (
    PQ_DATA_DIR, 
    PQ_DATA_UNDER_50, 
    PQ_DATA_50_69, 
    PQ_DATA_OVER_70, 
    MODEL_DIR
)
import _3a_PQmodel_algo_params as algo_params

# Import logic modules
import _3b_PQmodel_train as trainer
import _3c_PQmodel_Output as exporter

class ModelTrainingGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f5f5f5")
        self.parent = parent
        
        # Mapping for the selection dropdown
        self.category_map = {
            "ALL (Full Dataset)": PQ_DATA_DIR,
            "1. Under 50": PQ_DATA_UNDER_50,
            "2. 50 to 69": PQ_DATA_50_69,
            "3. Over 70": PQ_DATA_OVER_70
        }

        # Internal State
        self.pq_source_dir = PQ_DATA_DIR
        self.trained_results = None  
        self.current_sample_idx = 0

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        self._build_widgets()

    def _setup_styles(self):
        self.style.configure("Action.TButton", font=("Arial", 9, "bold"), padding=5)
        self.style.configure("TLabel", background="#f5f5f5", font=("Arial", 9))

    def _build_widgets(self):
        # --- 1. Top Panel: Path & Configuration ---
        top_frame = tk.Frame(self, bg="#f5f5f5")
        top_frame.pack(side="top", fill="x", padx=20, pady=10)

        # Data Selection Group
        path_group = tk.LabelFrame(top_frame, text=" 📂 Data Selection ", padx=15, pady=10, bg="white", font=("Arial", 10, "bold"))
        path_group.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Row 0: Category Selector
        tk.Label(path_group, text="Category:", bg="white").grid(row=0, column=0, sticky="w")
        self.combo_category = ttk.Combobox(path_group, values=list(self.category_map.keys()), state="readonly", width=20)
        self.combo_category.current(0)
        self.combo_category.grid(row=0, column=1, padx=10, sticky="w")
        self.combo_category.bind("<<ComboboxSelected>>", self.on_category_change)

        # Row 1: Current Path Display
        tk.Label(path_group, text="Path:", bg="white").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.lbl_source = tk.Label(path_group, text=self.pq_source_dir, fg="#0078d4", bg="white", font=("Consolas", 8))
        self.lbl_source.grid(row=1, column=1, padx=10, sticky="w", pady=(5,0))
        tk.Button(path_group, text="Browse", command=self.browse_source, bg="#e1e1e1", relief="flat", font=("Arial", 8)).grid(row=1, column=2, pady=(5,0))

        # Hyperparams Group
        config_group = tk.LabelFrame(top_frame, text=" ⚙️ Training Parameters ", padx=15, pady=10, bg="white", font=("Arial", 10, "bold"))
        config_group.pack(side="left", fill="both", padx=5)

        # --- Row 0: Epochs & Batch ---
        tk.Label(config_group, text="Epochs:", bg="white").grid(row=0, column=0, sticky="w")
        self.ent_epochs = tk.Entry(config_group, width=8, relief="solid", bd=1, justify="center")
        self.ent_epochs.insert(0, str(algo_params.DEFAULT_EPOCHS))
        self.ent_epochs.grid(row=0, column=1, padx=5)

        tk.Label(config_group, text="Batch:", bg="white").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.lbl_batch = tk.Label(config_group, text=str(algo_params.BATCH_SIZE), bg="white", font=("Arial", 9, "bold"))
        self.lbl_batch.grid(row=0, column=3, padx=5)

        # --- Row 1: Split Ratios (New) ---
        tk.Label(config_group, text="Ratio (Tr/Vl/Te):", bg="white").grid(row=1, column=0, sticky="w", pady=(10, 0))
        

        ratio_frame = tk.Frame(config_group, bg="white")
        ratio_frame.grid(row=1, column=1, columnspan=3, sticky="w", pady=(10, 0))

        # Train Ratio
        self.ent_train_r = tk.Entry(ratio_frame, width=4, relief="solid", bd=1, justify="center")
        self.ent_train_r.insert(0, "70")
        self.ent_train_r.pack(side="left")
        
        tk.Label(ratio_frame, text=":", bg="white").pack(side="left")

        # Val Ratio
        self.ent_val_r = tk.Entry(ratio_frame, width=4, relief="solid", bd=1, justify="center")
        self.ent_val_r.insert(0, "10")
        self.ent_val_r.pack(side="left")

        tk.Label(ratio_frame, text=":", bg="white").pack(side="left")

        # Test Ratio
        self.ent_test_r = tk.Entry(ratio_frame, width=4, relief="solid", bd=1, justify="center")
        self.ent_test_r.insert(0, "20")
        self.ent_test_r.pack(side="left")
        
        tk.Label(ratio_frame, text="%", bg="white").pack(side="left", padx=(2, 0))

        tk.Label(config_group, text="Epochs:", bg="white").grid(row=0, column=0, sticky="w")
        self.ent_epochs = tk.Entry(config_group, width=8, relief="solid", bd=1, justify="center")
        self.ent_epochs.insert(0, str(algo_params.DEFAULT_EPOCHS))
        self.ent_epochs.grid(row=0, column=1, padx=5)

        tk.Label(config_group, text="Batch:", bg="white").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.lbl_batch = tk.Label(config_group, text=str(algo_params.BATCH_SIZE), bg="white", font=("Arial", 9, "bold"))
        self.lbl_batch.grid(row=0, column=3, padx=5)

        # --- 2. Action Toolbar ---
        action_frame = tk.Frame(self, bg="#f5f5f5")
        action_frame.pack(side="top", fill="x", padx=20, pady=5)

        self.btn_train = tk.Button(action_frame, text="🚀 START MODEL TRAINING", command=self.on_start_training, 
                                 bg="#0078d4", fg="white", font=("Arial", 10, "bold"), padx=25, pady=8, relief="flat")
        self.btn_train.pack(side="left")

        self.btn_save = tk.Button(action_frame, text="💾 EXPORT MODEL WEIGHTS", command=self.on_export_model, 
                                 bg="#107c10", fg="white", font=("Arial", 10, "bold"), state="disabled", padx=25, pady=8, relief="flat")
        self.btn_save.pack(side="left", padx=15)

        # --- 3. Review & Navigation Bar ---
        self.nav_frame = tk.Frame(self, bg="#333333", pady=8)
        self.nav_frame.pack(side="top", fill="x", padx=20, pady=10)
        
        self.btn_prev = tk.Button(self.nav_frame, text="◀ PREV", command=self.prev_sample, state="disabled", bg="#555555", fg="white", relief="flat")
        self.btn_prev.pack(side="left", padx=20)
        
        self.lbl_info = tk.Label(self.nav_frame, text="IDLE - READY TO INITIALIZE", bg="#333333", fg="#00ff00", font=("Arial", 10, "bold"))
        self.lbl_info.pack(side="left", expand=True)
        
        self.btn_next = tk.Button(self.nav_frame, text="NEXT ▶", command=self.next_sample, state="disabled", bg="#555555", fg="white", relief="flat")
        self.btn_next.pack(side="left", padx=20)

        # --- 4. Main Display Area ---
        display_container = tk.Frame(self, bg="#f5f5f5")
        display_container.pack(side="top", fill="both", expand=True, padx=20, pady=5)

        # Plot Left
        plot_box = tk.LabelFrame(display_container, text=" PQ Performance Visualization ", bg="white", padx=5, pady=5)
        plot_box.pack(side="left", fill="both", expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_box)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Log Right
        log_box = tk.LabelFrame(display_container, text=" Training Console Log ", bg="white", padx=5, pady=5)
        log_box.pack(side="right", fill="y", padx=(15, 0))
        self.log_area = scrolledtext.ScrolledText(log_box, width=50, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

    # --- Logic Implementations ---
    def on_category_change(self, event):
        """Update data source based on selection."""
        selection = self.combo_category.get()
        self.pq_source_dir = self.category_map[selection]
        self.lbl_source.config(text=self.pq_source_dir)
        self.log(f"Category switched to: {selection}")

    def browse_source(self):
        path = filedialog.askdirectory(initialdir=self.pq_source_dir)
        if path:
            self.pq_source_dir = path
            self.lbl_source.config(text=path)
            self.log(f"Custom path selected: {path}")

    def log(self, text):
        self.log_area.insert(tk.END, f"[{algo_params.UNITS.get('speed', 'SYS')}] {text}\n")
        self.log_area.see(tk.END)
        self.update_idletasks()

    def on_start_training(self):
        try:
            epochs_str = self.ent_epochs.get()
            if not epochs_str.isdigit():
                raise ValueError("Epochs must be a valid integer.")
            
            epochs = int(epochs_str)
            self.log_area.delete('1.0', tk.END)
            self.log(f"Initializing AI Engine for: {self.combo_category.get()}...")
            self.btn_train.config(state="disabled", text="⏳ TRAINING...")
            
            # Call Backend Trainer with the selected data path
            # Make sure _3b_PQmodel_train.py accepts 'data_path' argument
            results = trainer.train(
                data_path=self.pq_source_dir,
                epochs=epochs, 
                gui_logger=self.log
            )
            
            if results:
                self.trained_results = results
                self.current_sample_idx = 0
                self.btn_save.config(state="normal")
                self.btn_prev.config(state="normal")
                self.btn_next.config(state="normal")
                self.update_review_display()
                self.log("Training sequence completed successfully.")
                messagebox.showinfo("Success", "Model training completed.")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Runtime Error", str(e))
        finally:
            self.btn_train.config(state="normal", text="🚀 START MODEL TRAINING")

    def on_export_model(self):
        """
        Triggered by the 'EXPORT MODEL WEIGHTS' button.
        Opens a popup window to collect model name and version before saving.
        """
        if not self.trained_results: 
            messagebox.showwarning("Warning", "No trained model found. Please train the model first.")
            return

        # 1. Create a Popup Window (Toplevel)
        save_win = tk.Toplevel(self)
        save_win.title("Export Configuration")
        save_win.geometry("320x220")
        save_win.configure(bg="white")
        save_win.grab_set()  # Focus all events to this window
        save_win.resizable(False, False)

        # Center the popup relative to the main window
        main_x = self.parent.winfo_x()
        main_y = self.parent.winfo_y()
        save_win.geometry(f"+{main_x + 400}+{main_y + 200}")

        # 2. Layout Elements inside the popup
        content_frame = tk.Frame(save_win, bg="white", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Model Name Input
        tk.Label(content_frame, text="Model Name (Series):", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        ent_name = tk.Entry(content_frame, width=30, relief="solid", bd=1)
        ent_name.insert(0, "A40")  # Default value
        ent_name.pack(pady=(0, 10))

        # Version Input
        tk.Label(content_frame, text="Version ID:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        ent_ver = tk.Entry(content_frame, width=30, relief="solid", bd=1)
        ent_ver.insert(0, "00")   # Default value
        ent_ver.pack(pady=(0, 15))

        # 3. Internal logic for the 'Confirm' button
        def execute_export():
            m_name = ent_name.get().strip()
            m_ver = ent_ver.get().strip()

            if not m_name or not m_ver:
                messagebox.showerror("Error", "Name and Version cannot be empty.")
                return

            try:
                self.log(f"Exporting files: {m_name}_{m_ver}...")
                res = self.trained_results
                
                # Call the logic from _3c_PQmodel_Output.py
                success = exporter.export_standalone(
                    model=res['model'], 
                    scaler=res['scaler'], 
                    feature_names=algo_params.FEATURE_ORDER,
                    model_name=m_name,
                    version=m_ver
                )
                
                if success:
                    self.log(f"[SUCCESS] Weights/Scaler/Config saved to {MODEL_DIR}")
                    messagebox.showinfo("Export Success", f"Model: {m_name}\nVersion: {m_ver}\nSuccessfully saved to disk.")
                    save_win.destroy()  # Close the popup
            except Exception as e:
                self.log(f"EXPORT FAILED: {str(e)}")
                messagebox.showerror("Export Failed", str(e))

        # 4. Confirm Button inside the popup
        btn_confirm = tk.Button(
            content_frame, 
            text="✔ CONFIRM & SAVE", 
            command=execute_export,
            bg="#107c10", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            pady=5, 
            relief="flat"
        )
        btn_confirm.pack(fill="x")

    def update_review_display(self):
        res = self.trained_results
        y_true = res['test_y'][self.current_sample_idx]
        y_pred = res['test_pred'][self.current_sample_idx]
        fan_name = res['test_names'][self.current_sample_idx]
        
        # Split P and Q
        p_true, q_true = y_true[:10], y_true[10:]
        p_pred, q_pred = y_pred[:10], y_pred[10:]
        
        mae = mean_absolute_error(y_true, y_pred)
        self.lbl_info.config(text=f"SAMPLE {self.current_sample_idx+1}/{len(res['test_y'])} | {fan_name} | MAE: {mae:.4f}")
        
        self.ax.clear()
        self.ax.plot(q_true, p_true, 'o-', label='Actual Data', color='#2ca02c', alpha=0.7, markersize=4)
        self.ax.plot(q_pred, p_pred, 'x--', label='AI Prediction', color='#d62728', linewidth=1.5)
        
        self.ax.set_title(f"PQ Curve Validation: {fan_name}", fontsize=10, fontweight='bold')
        self.ax.set_xlabel(f"Flow Rate ({algo_params.UNITS['flow']})")
        self.ax.set_ylabel(f"Static Pressure ({algo_params.UNITS['pressure']})")
        self.ax.legend(loc='upper right', fontsize=8)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        
        self.canvas.draw()

    def prev_sample(self):
        if self.current_sample_idx > 0:
            self.current_sample_idx -= 1
            self.update_review_display()

    def next_sample(self):
        if self.current_sample_idx < len(self.trained_results['test_y']) - 1:
            self.current_sample_idx += 1
            self.update_review_display()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fan AI Core - Professional Training Hub")
    root.geometry("1200x850")
    
    # Simple global styling for entries
    root.option_add("*Font", "Arial 9")
    
    gui = ModelTrainingGUI(root)
    gui.pack(fill="both", expand=True)
    root.mainloop()