# ================================================================================
# PROJECT: Fan Integrated Design Platform
# MODULE: _2g_Tip_Root_Rib_2D_Viewer.py
# DESCRIPTION: 
#   Updated to show ABSOLUTE height lift (Rake Angle Effect)
# ================================================================================
import os
import numpy as np
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SingleSectionSidePreview:
    def __init__(self, parent, title="", line_color="black"):
        self.fig = Figure(figsize=(4, 2.8), dpi=100, facecolor='#FFFFFF')
        self.ax = self.fig.add_subplot(111)
        self.line_color = line_color
        self.title = title
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_view(self, xyz_path):
        self.ax.clear()
        self.ax.set_title(self.title, fontsize=9, fontweight='bold')
        self.ax.set_xlabel("Arc Width (mm)", fontsize=8)
        self.ax.set_ylabel("Absolute Height Z (mm)", fontsize=8) # 顯示絕對高度
        self.ax.tick_params(labelsize=7)

        if not os.path.exists(xyz_path):
            self.ax.text(0.5, 0.5, "File Not Found", ha='center', va='center')
            self.canvas.draw()
            return

        try:
            data = np.loadtxt(xyz_path)
            if data.ndim == 1: data = data.reshape(1, -1)

            x, y, z = data[:, 0], data[:, 1], data[:, 2]
            
            # Calculate Cylindrical Mapping
            r_avg = np.mean(np.sqrt(x**2 + y**2))
            angles = np.arctan2(y, x)
            
            # Normalize angles relative to the first point to unroll
            rel_angles = angles - angles[0]
            rel_angles = (rel_angles + np.pi) % (2 * np.pi) - np.pi

            px = rel_angles * r_avg
            
            # --- KEY CHANGE HERE ---
            # Instead of z - min(z), we show the raw Z values 
            # so the Rake Angle lift is visible on the Y-axis.
            py = z 

            if len(px) > 0:
                px = np.append(px, px[0])
                py = np.append(py, py[0])

            self.ax.plot(px, py, color=self.line_color, linewidth=1.8)
            
            # --- VIEWPORT CONTROL ---
            # Use 'equal' aspect but allow the Y-axis to shift based on Z height
            self.ax.set_aspect('equal', adjustable='datalim')
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.ax.fill(px, py, color=self.line_color, alpha=0.05)

        except Exception as e:
            print(f"[Preview Error] {e}")

        self.fig.tight_layout()
        self.canvas.draw()