"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _1_fan_GUI.py
DESCRIPTION: 
    Fan design configuration interface. 
    Updates: 
    - Param Update: H (Height) -> CH (Chord Height)
    - New Param: HH (Hub Height)
    - Updated Bump / Stacking configuration based on latest algo_params.
================================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import traceback

# Core Modules
from _1d_XYZ_Output import BladeGenerator, rotate_xyz_with_prefix
from _1d1_creo import generate_creo_ibl
from _1e_STEP_Output import export_single_blade_step
from _1f_Blade_2D_Viewer import Blade2DPreview
from _1g_Tip_Root_Blade_2D_Viewer import SingleSectionSidePreview

from _1a_fan_path import (
    ensure_dirs, JSON_DIR, XYZ_ROOT_DIR, 
    XYZ_CREO_DIR, STEP_DIR, TEMPLATE_JSON
)

# --- Style Constants ---
CLR_PRIMARY = "#005EB8"  # Delta Blue
CLR_BG      = "#F1F5F9"  # Light background
CLR_CARD    = "#FFFFFF"  # White card
CLR_BORDER  = "#141414"  # Soft border
CLR_TEXT    = "#0F172A"  # Sharp text
CLR_SUBTEXT = "#64748B"  # Muted label

class FanGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CLR_BG)
        ensure_dirs()
        self.entries = {}
        self.status_var = tk.StringVar(value="System Ready")
        self.build_ui()
        self.auto_load_template()

    def build_ui(self):
        # Main Body Container
        body = tk.Frame(self, bg=CLR_BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- LEFT PANEL: Configuration ----------------
        left_panel = tk.Frame(body, bg=CLR_BG, width=420)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # --- Action Bar (Bottom of Left Panel) ---
        action_bar = tk.Frame(left_panel, bg=CLR_BG, pady=10)
        action_bar.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Main.TButton", font=("Segoe UI", 9, "bold"), background=CLR_PRIMARY, foreground="white", borderwidth=0)
        style.configure("Sub.TButton", font=("Segoe UI", 9), background="#E2E8F0", foreground=CLR_TEXT, borderwidth=0)

        sub_btn_frame = tk.Frame(action_bar, bg=CLR_BG)
        sub_btn_frame.pack(side="bottom", fill="x", pady=2)
        ttk.Button(sub_btn_frame, text="Load JSON", style="Sub.TButton", command=self.load_json).pack(side="left", expand=True, fill="x", padx=(0, 2))
        ttk.Button(sub_btn_frame, text="Save JSON", style="Sub.TButton", command=self.save_json).pack(side="left", expand=True, fill="x", padx=(2, 0))
        ttk.Button(action_bar, text="EXPORT STEP FILES", style="Sub.TButton", command=self.generate_step).pack(side="bottom", fill="x", pady=2)
        ttk.Button(action_bar, text="GENERATE & UPDATE PREVIEW", style="Main.TButton", command=self.generate_xyz).pack(side="bottom", fill="x", pady=2)

        # --- Parameter Panel ---
        self.param_card = tk.LabelFrame(left_panel, text="  PARAMETER DEFINITION  ", 
                                   font=("Segoe UI", 10, "bold"), fg=CLR_PRIMARY,
                                   bg=CLR_CARD, padx=10, pady=5, relief="flat", highlightthickness=1)
        self.param_card.config(highlightbackground=CLR_BORDER)
        self.param_card.pack(side="top", fill="x")
        self.param_card.columnconfigure(1, weight=1, minsize=180)

        # 1. Basic Spec (Added HH)
        self.create_header(self.param_card, "1. BASIC SPEC", 0)
        basic_fields = [
            ("Model Name", "MN"), ("Fan Width (mm)", "FW"), ("Fan Height (mm)", "FH"),
            ("Outer Diam (mm)", "OD"), ("Inner Diam (mm)", "ID"), ("Hub Height (mm)", "HH"), 
            ("Blade Count", "BC"), ("Clearance (mm)", "CG"), ("Rated Speed (RPM)", "RPM")
        ]
        curr_row = 1
        for label, key in basic_fields:
            self.add_grid_param(self.param_card, curr_row, label, key)
            curr_row += 1

        # 2-3. Airfoil (Root/Tip) (Changed H to CH)
        self.create_header(self.param_card, "2-3. AIRFOIL (ROOT / TIP)", curr_row)
        curr_row += 1
        airfoil_fields = [
            ("Chord Height (CH)", "R_CH", "T_CH"), ("Camber (ratio)", "R_CAM", "T_CAM"), 
            ("Camber Pos", "R_CP", "T_CP"), ("Max Thick (mm)", "R_TM", "T_TM"), 
            ("TE Thick (mm)", "R_TTE", "T_TTE"), ("Incidence (deg)", "R_IA", "T_IA"), 
            ("LE Offset (mm)", "R_LEO", "T_LEO")
        ]
        for label, k1, k2 in airfoil_fields:
            self.add_grid_param_pair(self.param_card, curr_row, label, k1, k2, "R", "T")
            curr_row += 1

        # 4. 3D & Stacking
        self.create_header(self.param_card, "4. 3D & STACKING", curr_row)
        curr_row += 1
        self.add_grid_param(self.param_card, curr_row, "F-angle (deg)", "FA"); curr_row += 1
        self.add_grid_param(self.param_card, curr_row, "Sharpness (S)", "S"); curr_row += 1
        self.add_grid_param_pair(self.param_card, curr_row, "Wave (Amp% / Cyc)", "Wave_Pct", "Wave_C", "%", "C"); curr_row += 1
        self.add_grid_param(self.param_card, curr_row, "Rise Angle (deg)", "Rise"); curr_row += 1
        
        # Surface Bump parameters
        self.add_grid_param_triple(self.param_card, curr_row, "Upper Bump (H/L/W)", "U1", "U2", "U3")
        curr_row += 1
        self.add_grid_param_triple(self.param_card, curr_row, "Lower Bump (H/L/W)", "L1", "L2", "L3")
        curr_row += 1

        # ---------------- RIGHT PANEL: Visualization ----------------
        right_panel = tk.Frame(body, bg=CLR_BG)
        right_panel.pack(side="right", fill="both", expand=True)

        # XY Projection Card
        top_box = tk.LabelFrame(right_panel, text="  XY PROJECTION  ", font=("Segoe UI", 9, "bold"), 
                               bg=CLR_CARD, fg=CLR_PRIMARY, relief="flat", highlightthickness=1)
        top_box.config(highlightbackground=CLR_BORDER)
        top_box.pack(fill="both", expand=True, pady=(0, 5))
        
        self.preview_f = Blade2DPreview(top_box)

        # Side Profiles Container
        side_container = tk.Frame(right_panel, bg=CLR_BG)
        side_container.pack(fill="x", side="bottom")

        for t, attr in [("ROOT (S0)", "preview_root"), ("TIP (SN)", "preview_tip")]:
            f = tk.LabelFrame(side_container, text=f"  {t}  ", font=("Segoe UI", 8, "bold"),
                             bg=CLR_CARD, fg=CLR_PRIMARY, relief="flat", highlightthickness=1)
            f.config(highlightbackground=CLR_BORDER)
            f.pack(side="left", fill="both", expand=True, padx=(0, 2) if "ROOT" in t else (2, 0))
            color = CLR_PRIMARY if "ROOT" in t else "#E11D48"
            setattr(self, attr, SingleSectionSidePreview(f, title="", line_color=color))

        status_bar = tk.Frame(self, bg=CLR_BORDER, height=20)
        status_bar.pack(side="bottom", fill="x")
        tk.Label(status_bar, textvariable=self.status_var, font=("Segoe UI", 8), bg=CLR_BORDER).pack(side="left", padx=10)

    # --- UI Helpers ---
    def create_header(self, parent, text, row):
        tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"), fg=CLR_SUBTEXT, bg=CLR_CARD).grid(row=row, column=0, columnspan=2, sticky="w", pady=(8, 2))

    def add_grid_param(self, parent, row, label, key):
        tk.Label(parent, text=label, font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD).grid(row=row, column=0, sticky="w")
        e = tk.Entry(parent, font=("Consolas", 10), justify="center", relief="flat", highlightthickness=1, highlightbackground=CLR_BORDER)
        e.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=1)
        self.entries[key] = e

    def add_grid_param_pair(self, parent, row, label, k1, k2, l1, l2):
        tk.Label(parent, text=label, font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD).grid(row=row, column=0, sticky="w")
        f = tk.Frame(parent, bg=CLR_CARD)
        f.grid(row=row, column=1, sticky="w", padx=(10, 0))
        for k, l in [(k1, l1), (k2, l2)]:
            tk.Label(f, text=l, font=("Segoe UI", 8, "italic"), fg=CLR_SUBTEXT, bg=CLR_CARD).pack(side="left", padx=2)
            e = tk.Entry(f, width=7, justify="center", relief="flat", highlightthickness=1, highlightbackground=CLR_BORDER)
            e.pack(side="left", padx=2)
            self.entries[k] = e

    def add_grid_param_triple(self, parent, row, label, k1, k2, k3):
        tk.Label(parent, text=label, font=("Segoe UI", 9), fg=CLR_TEXT, bg=CLR_CARD).grid(row=row, column=0, sticky="w")
        f = tk.Frame(parent, bg=CLR_CARD)
        f.grid(row=row, column=1, sticky="w", padx=(10, 0))
        for k, l in [(k1, "H"), (k2, "L"), (k3, "W")]:
            tk.Label(f, text=l, font=("Segoe UI", 7, "italic"), fg=CLR_SUBTEXT, bg=CLR_CARD).pack(side="left", padx=1)
            e = tk.Entry(f, width=5, justify="center", relief="flat", highlightthickness=1, highlightbackground=CLR_BORDER)
            e.pack(side="left", padx=1)
            self.entries[k] = e

    # --- Data Logic ---
    def _get_v(self, k):
        try: return float(self.entries[k].get() or 0)
        except: return 0.0

    def _collect_gui_data(self):
        """Builds a JSON-compatible dictionary using new parameter keys."""
        return {
            "basic": { 
                "MN": self.entries["MN"].get(), 
                "FW": self._get_v("FW"), "FH": self._get_v("FH"), 
                "OD": self._get_v("OD"), "ID": self._get_v("ID"), 
                "HH": self._get_v("HH"), "BC": int(self._get_v("BC")), 
                "CG": self._get_v("CG"), "RPM": self._get_v("RPM")
            },
            "airfoil_root": { 
                "CH": self._get_v("R_CH"), "CAM": self._get_v("R_CAM"), "CP": self._get_v("R_CP"), 
                "TM": self._get_v("R_TM"), "TTE": self._get_v("R_TTE"), "IA": self._get_v("R_IA"), 
                "LEO": self._get_v("R_LEO") 
            },
            "airfoil_tip": { 
                "CH": self._get_v("T_CH"), "CAM": self._get_v("T_CAM"), "CP": self._get_v("T_CP"), 
                "TM": self._get_v("T_TM"), "TTE": self._get_v("T_TTE"), "IA": self._get_v("T_IA"), 
                "LEO": self._get_v("T_LEO") 
            },
            "blade_3d": { 
                "FA": self._get_v("FA"), 
                "S": self._get_v("S"), 
                "Wave": [self._get_v("Wave_Pct"), self._get_v("Wave_C")], 
                "Rise": self._get_v("Rise"),
                "U_Bump": [self._get_v("U1"), self._get_v("U2"), self._get_v("U3")],
                "L_Bump": [self._get_v("L1"), self._get_v("L2"), self._get_v("L3")]
            }
        }

    def _fill_gui_from_data(self, data):
        """Fills entry fields from a JSON dictionary."""
        # 1. Basic
        b = data.get("basic", {})
        for k in ["MN", "FW", "FH", "OD", "ID", "HH", "BC", "CG", "RPM"]: 
            if k in self.entries: 
                self.entries[k].delete(0, tk.END)
                self.entries[k].insert(0, str(b.get(k, "")))
        
        # 2-3. Airfoils (Mapping CH and others)
        r, t = data.get("airfoil_root", {}), data.get("airfoil_tip", {})
        # Handle backward compatibility: check for 'H' if 'CH' is missing
        for k in ["CH", "CAM", "CP", "TM", "TTE", "IA", "LEO"]:
            val_r = r.get(k) if r.get(k) is not None else r.get("H", "")
            val_t = t.get(k) if t.get(k) is not None else t.get("H", "")
            
            self.entries[f"R_{k}"].delete(0, tk.END)
            self.entries[f"R_{k}"].insert(0, str(val_r))
            self.entries[f"T_{k}"].delete(0, tk.END)
            self.entries[f"T_{k}"].insert(0, str(val_t))
            
        # 4. 3D Stacking
        d = data.get("blade_3d", {})
        for k in ["FA", "S", "Rise"]:
            if k in self.entries:
                self.entries[k].delete(0, tk.END)
                self.entries[k].insert(0, str(d.get(k, "")))
        
        wv = d.get("Wave", [0.0, 1.0])
        self.entries["Wave_Pct"].delete(0, tk.END); self.entries["Wave_Pct"].insert(0, str(wv[0]))
        self.entries["Wave_C"].delete(0, tk.END); self.entries["Wave_C"].insert(0, str(wv[1]))

        bmp_u = d.get("U_Bump", [0, 0, 1])
        for i, k in enumerate(["U1", "U2", "U3"]): 
            self.entries[k].delete(0, tk.END); self.entries[k].insert(0, str(bmp_u[i]))
        bmp_l = d.get("L_Bump", [0, 0, 1])
        for i, k in enumerate(["L1", "L2", "L3"]): 
            self.entries[k].delete(0, tk.END); self.entries[k].insert(0, str(bmp_l[i]))

    def generate_xyz(self):
        try:
            current_data = self._collect_gui_data()
            with open(TEMPLATE_JSON, "w", encoding="utf-8") as f: 
                json.dump(current_data, f, indent=2)
            
            # Reload algo params
            import _1a_fan_algo_params as AP
            AP.load_from_json(TEMPLATE_JSON)

            gen = BladeGenerator(TEMPLATE_JSON)
            gen.export_xyz(XYZ_ROOT_DIR)
            
            rotate_xyz_with_prefix(XYZ_ROOT_DIR, int(self._get_v("BC")))
            generate_creo_ibl(source_folder=XYZ_ROOT_DIR, output_folder=XYZ_CREO_DIR)
            
            self.preview_f.update_from_xyz_dir(XYZ_ROOT_DIR, self._get_v("FW"), self._get_v("FH"),
                                              self._get_v("OD"), self._get_v("ID"), self._get_v("CG"))
            
            mn = self.entries["MN"].get()
            sec_count = int(getattr(AP, "SECTION_COUNT", 10))
            self.preview_root.update_view(os.path.join(XYZ_ROOT_DIR, f"1_{mn}_Section0.txt"))
            self.preview_tip.update_view(os.path.join(XYZ_ROOT_DIR, f"1_{mn}_Section{sec_count-1}.txt"))
            
            self.status_var.set("Update Successful (Updated CH & HH Parameters)")
        except Exception: 
            traceback.print_exc()
            self.status_var.set("Update Failed. Check Console.")

    def generate_step(self):
        os.makedirs(STEP_DIR, exist_ok=True)
        try:
            data = self._collect_gui_data()
            mn, bc = data["basic"]["MN"], int(data["basic"]["BC"])
            for i in range(1, bc + 1):
                export_single_blade_step(XYZ_ROOT_DIR, os.path.join(STEP_DIR, f"{i}_{mn}.step"), f"{i}_{mn}")
            messagebox.showinfo("Success", "STEP exported.")
        except: 
            messagebox.showerror("Error", "Export failed.")

    def load_json(self):
        path = filedialog.askopenfilename(initialdir=JSON_DIR, filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f: 
                self._fill_gui_from_data(json.load(f))
            self.status_var.set(f"Loaded: {os.path.basename(path)}")

    def save_json(self):
        fn = filedialog.asksaveasfilename(initialdir=JSON_DIR, defaultextension=".json")
        if fn:
            with open(fn, "w", encoding="utf-8") as f: 
                json.dump(self._collect_gui_data(), f, indent=2)
            self.status_var.set(f"Saved: {os.path.basename(fn)}")

    def auto_load_template(self):
        if os.path.exists(TEMPLATE_JSON):
            with open(TEMPLATE_JSON, "r") as f: 
                self._fill_gui_from_data(json.load(f))
        self.status_var.set("Ready.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fan Integrated Design Platform")
    root.geometry("1200x950")
    FanGUI(root).pack(fill="both", expand=True)
    root.mainloop()