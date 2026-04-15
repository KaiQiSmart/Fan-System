# ================================================================================
# PROJECT: Fan Integrated Design Platform
# MODULE: _2_rib_GUI.py
# DESCRIPTION:
#     Rib design configuration interface (Trapezoidal Rib System)
# ================================================================================
import tkinter as tk
from tkinter import ttk, filedialog
from _2d1_XYZ_creo import generate_full_creo_ibl
import json
import os
import traceback
import glob

# --- Path & Core Rib Modules ---
from _2a_rib_path import ensure_dirs, JSON_DIR, XYZ_ROOT_DIR, XYZ_CREO_DIR
import _2a_rib_algo_params as AP
from _2d_XYZ_Output import RibXYZGenerator, rotate_ribs_with_prefix
from _2f_rib_2D_Viewer import Rib2DPreview
from _2g_Tip_Root_Rib_2D_Viewer import SingleSectionSidePreview

# --- Style Constants ---
CLR_PRIMARY = "#005EB8"
CLR_BG      = "#F1F5F9"
CLR_CARD    = "#FFFFFF"
CLR_BORDER  = "#CBD5E1"
CLR_TEXT    = "#0F172A"
CLR_SUBTEXT = "#64748B"


class RibGUI(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=CLR_BG)
        ensure_dirs()

        self.entries = {}
        self.status_var = tk.StringVar(value="Rib System Ready")

        self.output_dir = XYZ_ROOT_DIR
        
        self.template_json = os.path.join(JSON_DIR, "rib_template.json")

        self.build_ui()
        self.auto_load_template()

    # ============================================================================
    # UI BUILD
    # ============================================================================
    def build_ui(self):
        body = tk.Frame(self, bg=CLR_BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- LEFT PANEL (Parameters) ----------------
        left_panel = tk.Frame(body, bg=CLR_BG, width=450)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        action_bar = tk.Frame(left_panel, bg=CLR_BG, pady=10)
        action_bar.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Main.TButton",
            font=("Segoe UI", 10, "bold"),
            background=CLR_PRIMARY,
            foreground="white",
        )
        style.configure(
            "Sub.TButton",
            font=("Segoe UI", 9),
            background="#E2E8F0",
            foreground=CLR_TEXT,
        )

        sub_btn_frame = tk.Frame(action_bar, bg=CLR_BG)
        sub_btn_frame.pack(side="bottom", fill="x", pady=2)

        ttk.Button(
            sub_btn_frame, text="📁 Load JSON", style="Sub.TButton",
            command=self.load_json
        ).pack(side="left", expand=True, fill="x", padx=(0, 2))

        ttk.Button(
            sub_btn_frame, text="💾 Save JSON", style="Sub.TButton",
            command=self.save_json
        ).pack(side="left", expand=True, fill="x", padx=(2, 0))

        ttk.Button(
            action_bar,
            text="🚀 GENERATE RIB & UPDATE PREVIEW",
            style="Main.TButton",
            command=self.generate_rib_xyz
        ).pack(side="bottom", fill="x", pady=5)

        self.param_card = tk.LabelFrame(
            left_panel,
            text="  RIB PARAMETER DEFINITION  ",
            font=("Segoe UI", 10, "bold"),
            fg=CLR_PRIMARY,
            bg=CLR_CARD,
            padx=15,
            pady=10,
            relief="flat",
            highlightthickness=1
        )
        self.param_card.config(highlightbackground=CLR_BORDER)
        self.param_card.pack(side="top", fill="both", expand=True)
        self.param_card.columnconfigure(1, weight=1, minsize=180)

        # ---------------- PARAMETERS GRID ----------------
        self.create_header(self.param_card, "1. BASIC SPECIFICATION", 0)
        row = 1
        
        for label, key in [
            ("Model Name", "MN"),
            ("Fan Width (mm)", "FW"),
            ("Fan Height (mm)", "FH"),
            ("Outer Diam (mm)", "OD"),
            ("Inner Diam (mm)", "ID"),
            ("Rib Count (Array)", "RC"),
            ("Rib Type (0:Str, 1:Spi)", "RT"), 
        ]:
            self.add_grid_param(self.param_card, row, label, key)
            row += 1

        self.create_header(self.param_card, "2–3. RIB PROFILE (ROOT vs TIP)", row)
        row += 1
        for label, r_k, t_k in [
            ("Rib Height (RH)", "R_RH", "T_RH"),
            ("Leading Angle (LA)", "R_LA", "T_LA"),
            ("Top Width (TW)", "R_TW", "T_TW"),
            ("Top Radius (TR)", "R_TR", "T_TR"),
            ("Bot Width (BW)", "R_BW", "T_BW"),
            ("Bot Radius (BR)", "R_BR", "T_BR"),
        ]:
            self.add_grid_param_pair(self.param_card, row, label, r_k, t_k, "Root", "Tip")
            row += 1

        self.create_header(self.param_card, "4. 3D STACKING & RAKE", row)
        row += 1
        self.add_grid_param(self.param_card, row, "Flare Angle (FA deg)", "FA")
        row += 1
        self.add_grid_param(self.param_card, row, "Rake Angle (RAKE deg)", "RAKE")

        # ---------------- RIGHT PANEL (Visualizer) ----------------
        right_panel = tk.Frame(body, bg=CLR_BG)
        right_panel.pack(side="right", fill="both", expand=True)

        top_box = tk.LabelFrame(
            right_panel,
            text="  XY WIREFRAME PROJECTION  ",
            font=("Segoe UI", 9, "bold"),
            bg=CLR_CARD,
            fg=CLR_PRIMARY,
            relief="flat",
            highlightthickness=1
        )
        top_box.config(highlightbackground=CLR_BORDER)
        top_box.pack(fill="both", expand=True, pady=(0, 5))
        self.preview_f = Rib2DPreview(top_box)

        side_container = tk.Frame(right_panel, bg=CLR_BG)
        side_container.pack(fill="x", side="bottom")

        for title, attr, color in [
            ("ROOT SECTION (S0)", "preview_root", CLR_PRIMARY),
            ("TIP SECTION (SN)", "preview_tip", "#E11D48"),
        ]:
            f = tk.LabelFrame(
                side_container,
                text=f"  {title}  ",
                font=("Segoe UI", 8, "bold"),
                bg=CLR_CARD,
                fg=CLR_PRIMARY,
                relief="flat",
                highlightthickness=1
            )
            f.config(highlightbackground=CLR_BORDER)
            f.pack(side="left", fill="both", expand=True, padx=2)
            setattr(self, attr, SingleSectionSidePreview(f, title="", line_color=color))

        status_bar = tk.Frame(self, bg=CLR_BORDER, height=25)
        status_bar.pack(side="bottom", fill="x")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=CLR_BORDER,
            fg=CLR_TEXT
        ).pack(side="left", padx=10)

    # ============================================================================
    # UI HELPERS
    # ============================================================================
    def create_header(self, parent, text, row):
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 8, "bold"),
            fg=CLR_SUBTEXT,
            bg=CLR_CARD
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 4))

    def add_grid_param(self, parent, row, label, key):
        tk.Label(parent, text=label, bg=CLR_CARD, font=("Segoe UI", 9)).grid(row=row, column=0, sticky="w", pady=2)
        e = tk.Entry(parent, justify="center", font=("Consolas", 10), relief="solid", borderwidth=1)
        e.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.entries[key] = e

    def add_grid_param_pair(self, parent, row, label, k1, k2, l1, l2):
        tk.Label(parent, text=label, bg=CLR_CARD, font=("Segoe UI", 9)).grid(row=row, column=0, sticky="w", pady=2)
        f = tk.Frame(parent, bg=CLR_CARD)
        f.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
        
        for k, l in [(k1, l1), (k2, l2)]:
            tk.Label(f, text=f"{l}:", bg=CLR_CARD, font=("Segoe UI", 8)).pack(side="left", padx=(5, 2))
            e = tk.Entry(f, width=8, justify="center", font=("Consolas", 10), relief="solid", borderwidth=1)
            e.pack(side="left")
            self.entries[k] = e

    def _get_v(self, k):
        try:
            val = self.entries[k].get().strip()
            return float(val) if val else 0.0
        except Exception:
            return 0.0

    # ============================================================================
    # CORE LOGIC
    # ============================================================================
    def _collect_gui_data(self):
        rc = int(self._get_v("RC"))
        rt = int(self._get_v("RT")) 
        return {
            "basic": {
                "MN": self.entries["MN"].get() or "DefaultModel",
                "FW": self._get_v("FW"),
                "FH": self._get_v("FH"),
                "OD": self._get_v("OD"),
                "ID": self._get_v("ID"),
                "RC": rc,
                "RT": rt, 
                "SECTION_COUNT": 10,
            },
            "rib_root": {
                "RH": self._get_v("R_RH"),
                "LA": self._get_v("R_LA"),
                "TW": self._get_v("R_TW"),
                "TR": self._get_v("R_TR"),
                "BW": self._get_v("R_BW"),
                "BR": self._get_v("R_BR"),
            },
            "rib_tip": {
                "RH": self._get_v("T_RH"),
                "LA": self._get_v("T_LA"),
                "TW": self._get_v("T_TW"),
                "TR": self._get_v("T_TR"),
                "BW": self._get_v("T_BW"),
                "BR": self._get_v("T_BR"),
            },
            "rib_3d": {
                "FA": self._get_v("FA"),
                "RAKE": self._get_v("RAKE"),
            }
        }

    def generate_rib_xyz(self):
        try:
            data = self._collect_gui_data()
            mn = data["basic"]["MN"]
            rc = data["basic"]["RC"]
            sec_n = data["basic"]["SECTION_COUNT"]

            with open(self.template_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
           
            AP.load_from_json(self.template_json)

           
            gen = RibXYZGenerator()
            gen.export_xyz(self.output_dir)

            rotate_ribs_with_prefix(self.output_dir, rc)
            generate_full_creo_ibl(source_folder=XYZ_ROOT_DIR, output_folder=XYZ_CREO_DIR)
            
            self.preview_f.update_from_xyz_dir(
                self.output_dir,
                self._get_v("FW"),
                self._get_v("OD"),
                self._get_v("ID")
            )

            root_file = f"1_{mn}_RibSection0.txt"
            tip_file  = f"1_{mn}_RibSection{sec_n-1}.txt"
            root_path = os.path.join(self.output_dir, root_file)
            tip_path  = os.path.join(self.output_dir, tip_file)

            if not os.path.exists(root_path):
                g = glob.glob(os.path.join(self.output_dir, f"{mn}_RibSection0.txt"))
                if g: root_path = g[0]
            
            if not os.path.exists(tip_path):
                g = glob.glob(os.path.join(self.output_dir, f"{mn}_RibSection{sec_n-1}.txt"))
                if g: tip_path = g[0]

            if os.path.exists(root_path):
                self.preview_root.update_view(root_path)
            if os.path.exists(tip_path):
                self.preview_tip.update_view(tip_path)

            self.status_var.set(f"✅ SUCCESS: Generated {rc} ribs ({mn}). Profiles updated.")

        except Exception as e:
            traceback.print_exc()
            self.status_var.set(f"❌ ERROR: {str(e)}")

    def load_json(self):
        path = filedialog.askopenfilename(
            initialdir=JSON_DIR, filetypes=[("JSON files", "*.json")]
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._fill_gui_from_data(json.load(f))
                self.status_var.set(f"Loaded: {os.path.basename(path)}")
            except Exception as e:
                self.status_var.set(f"Load Error: {e}")

    def save_json(self):
        fn = filedialog.asksaveasfilename(
            initialdir=JSON_DIR, defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if fn:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(self._collect_gui_data(), f, indent=2)
            self.status_var.set(f"Saved: {os.path.basename(fn)}")

    def _fill_gui_from_data(self, data):
        # Basic
        b = data.get("basic", {})
        for k in ["MN", "FW", "FH", "OD", "ID", "RC", "RT"]: 
            if k in self.entries:
                self.entries[k].delete(0, tk.END)
                self.entries[k].insert(0, str(b.get(k, "")))

        # Rib Root & Tip
        for block, prefix in [("rib_root", "R_"), ("rib_tip", "T_")]:
            sec = data.get(block, {})
            for k in ["RH", "LA", "TW", "TR", "BW", "BR"]:
                ek = prefix + k
                if ek in self.entries:
                    self.entries[ek].delete(0, tk.END)
                    self.entries[ek].insert(0, str(sec.get(k, "")))

        # Stacking
        d3 = data.get("rib_3d", {})
        for k in ["FA", "RAKE"]:
            if k in self.entries:
                self.entries[k].delete(0, tk.END)
                self.entries[k].insert(0, str(d3.get(k, "")))

    def auto_load_template(self):
        if os.path.exists(self.template_json):
            try:
                with open(self.template_json, "r", encoding="utf-8") as f:
                    self._fill_gui_from_data(json.load(f))
            except Exception:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fan Integrated Design Platform | Trapezoidal Rib System")
    root.geometry("1200x900")
    
    app = RibGUI(root)
    app.pack(fill="both", expand=True)
    root.mainloop()