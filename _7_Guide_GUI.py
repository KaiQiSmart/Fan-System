"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _7_Guide_GUI.py
DESCRIPTION: 
    Updated Documentation module. 
    Synchronized with _1a_fan_algo_params.py (CH, HH, RPM, BUMP).
    Provides detailed range constraints and design insights.
================================================================================
"""

import tkinter as tk
from tkinter import ttk

# --- Style Constants ---
CLR_PRIMARY = "#005EB8"  # Delta Blue
CLR_BG      = "#FFFFFF"  # White background
CLR_TEXT    = "#1E293B"  # Main text
CLR_BORDER  = "#E2E8F0"

class ParameterGuideGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CLR_BG)
        self.build_ui()

    def build_ui(self):
        # Container with padding
        container = tk.Frame(self, bg=CLR_BG, padx=30, pady=30)
        container.pack(fill="both", expand=True)

        # 1. Header Section
        header = tk.Frame(container, bg=CLR_BG)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="FAN ALGORITHM PARAMETER REFERENCE GUIDE", 
                 font=("Segoe UI", 18, "bold"), fg=CLR_PRIMARY, bg=CLR_BG).pack(side="left")

        # 2. Setup Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=32, foreground=CLR_TEXT)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#F8FAFC")

        # 3. Create Treeview for Table display
        columns = ("parameter", "description", "range", "note")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="none")
        
        # Define Headings
        self.tree.heading("parameter", text="Parameter")
        self.tree.heading("description", text="Physical Description")
        self.tree.heading("range", text="Recommended Range / Unit")
        self.tree.heading("note", text="Design Insight / Constraint")

        # Define Column Widths
        self.tree.column("parameter", width=140, anchor="w")
        self.tree.column("description", width=320, anchor="w")
        self.tree.column("range", width=200, anchor="center")
        self.tree.column("note", width=350, anchor="w")

        # 4. Insert Data
        self.insert_data()

        # Scrollbar logic
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def insert_data(self):
        """Standardized Parameter Ranges based on latest IVFBU Fan Design Standards."""
        
        data = [
            ("1. BASIC SPECIFICATIONS (Global Geometry)", [
                ("MN", "Model Name", "String", "Unique ID for file naming (e.g., 'A4010')"),
                ("FW / FH", "Fan Frame Width / Height", "10.0 - 200.0 (mm)", "Physical frame size constraints"),
                ("OD", "Outer Diameter (Tip)", " < FW - 2*CG ", "Must be smaller than frame width"),
                ("ID", "Inner Diameter (Hub)", " > 10.0 (mm) ", "Limited by motor and bearing size"),
                ("HH", "Hub Height", "0.0 - FH (mm)", "Determines the vertical seat of the hub"),
                ("BC", "Blade Count", "3, 5, 7, 9, 11, 13", "Usually odd numbers to reduce vibration"),
                ("CG", "Clearance Gap", "0.3 - 1.5 (mm)", "Gap between tip and frame; smaller = better P-Q"),
                ("RPM", "Rated Speed", "500 - 30000 (RPM)", "Rated Speed for Specific Model(Does not affect blade geometry)"),
            ]),
            ("2. AIRFOIL - TIP SECTION (T_)", [
                ("T_CH", "Tip Chord Height", "> 0.0 (mm)", "Projected vertical height of the airfoil"),
                ("T_CAM", "Tip Camber Ratio", "0.0 - 1.0", "0 = Flat plate; Higher = More pressure"),
                ("T_CP", "Tip Camber Position", "0.0 - 1.0", "Usually 0.4 (40% from leading edge)"),
                ("T_TM", "Tip Max Thickness", "> 0.0 (mm)", "Structural integrity at high RPM"),
                ("T_TTE", "Tip TE Thickness", "> 0.0 (mm)", "Trailing edge thickness; Affects noise"),
                ("T_IA", "Tip Incidence Angle", "0.0 - 90.0 (deg)", "Angle relative to rotation plane"),
                ("T_LEO", "Tip LE Offset", "-5.0 - 5.0 (mm)", "Leading edge shift along X-axis"),
            ]),
            ("3. AIRFOIL - ROOT SECTION (R_)", [
                ("R_CH", "Root Chord Height", "> 0.0 (mm)", "Usually T_CH = R_CH for linear blades"),
                ("R_CAM", "Root Camber Ratio", "0.0 - 1.0", "Root usually has higher camber than Tip"),
                ("R_CP", "Root Camber Position", "0.0 - 1.0", "Position of maximum lift"),
                ("R_TM", "Root Max Thickness", "> 0.0 (mm)", "Must be thicker than Tip for root strength"),
                ("R_TTE", "Root TE Thickness", "> 0.0 (mm)", "Trailing edge thickness at hub"),
                ("R_IA", "Root Incidence Angle", "0.0 - 90.0 (deg)", "Constraint: R_IA > T_IA (Twist)"),
                ("R_LEO", "Root LE Offset", "-5.0 - 5.0 (mm)", "LE shift at hub connection"),
            ]),
            ("4. 3D STACKING & BUMP PARAMETERS", [
                ("FA", "F-Angle (Sweep)", "-90.0 - 90.0 (deg)", "(+) Forward / (-) Backward Sweep"),
                ("S", "Blade Sharpness", "0.0 - 50.0", "Determines LE/TE curvature sharpness"),
                ("WAVE", "Stacking Wave", "[0-100%, 0-4]", "Amp (as % of CH) and Cycles"),
                ("RISE", "Rise Angle (Dihedral)", "-90.0 - 90.0 (deg)", "Out-of-plane tilt of the blade"),
                ("U_BUMP", "Upper Surface Ripple", "[A, L, W]", "A(0-1), L(0-1), W(0-2); 0=Disabled"),
                ("L_BUMP", "Lower Surface Ripple", "[A, L, W]", "A(0-1), L(0-1), W(0-2); 0=Disabled"),
            ]),
            ("ALGORITHM SETTINGS", [
                ("SECTION_COUNT", "Interpolation Count", "10", "Number of 2D slices to build 3D loft"),
                ("_A0 ~ _A4", "NACA Constants", "Fixed", "Standard NACA 4-digit thickness coefficients"),
            ])
        ]

        for group_name, items in data:
            # Insert Group Header
            self.tree.insert("", tk.END, values=(group_name, "", "", ""), tags=("group",))
            for item in items:
                self.tree.insert("", tk.END, values=item)

        # Visual styling for category headers
        self.tree.tag_configure("group", background="#E2E8F0", font=("Segoe UI", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Standard Parameter Guide")
    root.geometry("1150x850")
    app = ParameterGuideGUI(root)
    app.pack(fill="both", expand=True)
    root.mainloop()