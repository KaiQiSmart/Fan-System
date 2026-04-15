# ==================================================
# _1f_Blade_2D_Viewer.py
# Blade 2D Viewer (WIRE FRAME ONLY)
#
# Responsibilities:
# - Project XYZ to XY (Ignore Z)
# - Connect identical point indices across ALL sections
# - Highlight Hub (S0) and Tip (S_last)
# ==================================================

import os
import re
import numpy as np
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Rectangle

def parse_blade_info(filename):
    """
    Parses '1_A4020P_1_Section0.txt' -> Blade 1, Section 0
    """
    m = re.match(r"(\d+)_.*_Section(\d+)\.(txt|xyz)$", filename, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

class Blade2DPreview:
    def __init__(self, parent):
        fig = Figure(figsize=(5.5, 5.5), dpi=100)
        self.fig = fig
        self.ax = fig.add_subplot(111)
        self.ax.set_aspect("equal")

        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_from_xyz_dir(self, xyz_dir, FW, FH, OD, ID, CG):
        # Dictionary structure: blades[blade_id][section_id] = xy_array
        blades = defaultdict(dict)

        if not os.path.exists(xyz_dir):
            return

        # 1. Load data and project to XY (Ignore Z)
        for fn in os.listdir(xyz_dir):
            info = parse_blade_info(fn)
            if not info: continue
            
            b_idx, s_idx = info
            try:
                data = np.loadtxt(os.path.join(xyz_dir, fn))
                if data.ndim == 1: data = data.reshape(1, -1)
                # Store XY coordinates
                blades[b_idx][s_idx] = data[:, :2]
            except:
                continue

        if not blades:
            return

        # 2. Geometry Parameters
        FW, OD, ID, CG = map(float, [FW, OD, ID, CG])
        half_fw, hub_r, tip_r = FW/2.0, ID/2.0, OD/2.0
        housing_r = tip_r + CG

        # 3. Setup Canvas
        self.ax.clear()
        self.ax.set_aspect("equal")
        self.ax.set_title("Blade Wireframe: Spanwise Flowlines", fontsize=9, fontweight='bold')

        # Draw Housing Environment (Grey frame, White air-path)
        self.ax.add_patch(Rectangle((-half_fw, -half_fw), FW, FW, facecolor="#f5f5f5", edgecolor="#333", zorder=0))
        self.ax.add_patch(Circle((0, 0), housing_r, facecolor="white", edgecolor="#333", zorder=1))

        # 4. Process Each Blade
        for b_idx in sorted(blades.keys()):
            sections = blades[b_idx]
            sorted_s_ids = sorted(sections.keys())
            if not sorted_s_ids: continue

            # --- A. Draw Structural Flowlines ---
            # Connect the i-th point of S0, S1, S2... S_last
            num_pts_per_sec = len(sections[sorted_s_ids[0]])
            
            # Use every single point to form lines (No step-size skipping)
            for i in range(num_pts_per_sec): 
                # Create a line through all available sections for this point index
                line_x = [sections[sid][i, 0] for sid in sorted_s_ids if i < len(sections[sid])]
                line_y = [sections[sid][i, 1] for sid in sorted_s_ids if i < len(sections[sid])]
                
                # Draw the flowline with low alpha for a professional wireframe look
                self.ax.plot(line_x, line_y, color="#2c3e50", linewidth=0.5, alpha=0.4, zorder=4)

            # --- B. Draw Individual Section Borders (Key frames) ---
            # S0 = Hub (Black), S_last = Tip (Red)
            for sid in [sorted_s_ids[0], sorted_s_ids[-1]]:
                s_pts = sections[sid]
                sx = np.append(s_pts[:, 0], s_pts[0, 0])
                sy = np.append(s_pts[:, 1], s_pts[0, 1])
                
                is_tip = (sid == sorted_s_ids[-1])
                color = "#e74c3c" if is_tip else "#2c3e50"
                self.ax.plot(sx, sy, color=color, linewidth=1.2, zorder=5)

        # 5. Draw Hub & Finalize
        self.ax.add_patch(Circle((0, 0), hub_r, facecolor="#113D58", edgecolor="#0B3560", zorder=10))
        
        limit = half_fw * 1.1
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.axis("off")
        
        self.canvas.draw()