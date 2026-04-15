# ==================================================
# _1g_Tip_Root_Blade_2D_Viewer.py
# Independent Section Side-View (Chord-Z Plane)
# ==================================================

import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SingleSectionSidePreview:
    def __init__(self, parent, title="Section Preview", line_color="black"):
        
        fig = Figure(figsize=(4, 2.5), dpi=100)
        self.fig = fig
        self.ax = fig.add_subplot(111)
        self.line_color = line_color
        self.title_text = title
        
        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _project_and_align(self, pts_3d):
        
        if len(pts_3d) < 2: return np.zeros((2, 2))
        
        pts_2d = pts_3d[:, :2]
        
      
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(pts_2d))
        i, j = np.unravel_index(np.argmax(dist_matrix), dist_matrix.shape)
        
        p1, p2 = pts_2d[i], pts_2d[j]
        chord_vec = p2 - p1
        angle = np.arctan2(chord_vec[1], chord_vec[0])
        
        
        cos_a, sin_a = np.cos(-angle), np.sin(-angle)
        rot_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        
        pts_centered = pts_2d - p1
        x_prime = pts_centered @ rot_matrix.T
        
      
        return np.column_stack((x_prime[:, 0], pts_3d[:, 2]))

    def update_view(self, xyz_path):
        
        self.ax.clear()
        self.ax.set_title(self.title_text, fontsize=9, fontweight='bold')
        self.ax.set_xlabel("Chord (mm)", fontsize=8)
        self.ax.set_ylabel("Z (mm)", fontsize=8)
        self.ax.grid(True, linestyle=':', alpha=0.4)

        if not os.path.exists(xyz_path):
            self.ax.text(0.5, 0.5, "Wait for Gen...", ha='center', color='gray')
            self.canvas.draw()
            return

        try:
            data = np.loadtxt(xyz_path)
            if data.ndim == 1: data = data.reshape(1, -1)
            
            
            proj_data = self._project_and_align(data)
            
            
            self.ax.plot(proj_data[:, 0], proj_data[:, 1], color=self.line_color, linewidth=1.5)
            
            
            self.ax.set_aspect('equal', adjustable='datalim')
            
        except Exception as e:
            print(f"Error loading section: {e}")

        self.canvas.draw()