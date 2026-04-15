# ================================================================================
# _2f_rib_2D_Viewer.py
# Rib 2D Wireframe + Filled Ribs Viewer (Radial Stacking)
# ================================================================================

import os
import re
import numpy as np
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from _2a_rib_path import XYZ_ROOT_DIR


def parse_rib_info(filename):
    m = re.match(r"(\d+)_.*_RibSection(\d+)\.(txt|xyz)$", filename, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


class Rib2DPreview:
    def __init__(self, parent):
        fig = Figure(figsize=(5.5, 5.5), dpi=100)
        self.fig = fig
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_from_xyz_dir(self, xyz_dir, FW, OD, ID):
        ribs = defaultdict(dict)
        if not os.path.exists(xyz_dir):
            return

        for fn in os.listdir(xyz_dir):
            info = parse_rib_info(fn)
            if not info:
                continue
            r_idx, s_idx = info
            try:
                data = np.loadtxt(os.path.join(xyz_dir, fn))
                if data.ndim == 1:
                    data = data.reshape(1, -1)
                ribs[r_idx][s_idx] = data[:, :2]
            except:
                continue

        if not ribs:
            return

        self.ax.clear()
        self.ax.set_aspect("equal")
        self.ax.set_title("Rib Wireframe: Radial Stacking", fontsize=9, fontweight="bold")

        hub_r = float(ID) / 2.0
        tip_r = float(OD) / 2.0
        fw = float(FW)
        half_fw = fw / 2.0

        # ===================================================
        # Shaded region: FW square minus OD circle
        # ===================================================
        theta = np.linspace(0, 2 * np.pi, 240)

        square_vertices = np.array([
            (-half_fw, -half_fw),
            ( half_fw, -half_fw),
            ( half_fw,  half_fw),
            (-half_fw,  half_fw),
            (-half_fw, -half_fw),
        ])
        square_codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

        circle_vertices = np.column_stack((
            tip_r * np.cos(theta[::-1]),
            tip_r * np.sin(theta[::-1])
        ))
        circle_vertices = np.vstack([circle_vertices, circle_vertices[0]])
        circle_codes = (
            [Path.MOVETO]
            + [Path.LINETO] * (len(circle_vertices) - 2)
            + [Path.CLOSEPOLY]
        )

        vertices = np.vstack([square_vertices, circle_vertices])
        codes = square_codes + circle_codes

        patch = PathPatch(
            Path(vertices, codes),
            facecolor="#cfe2ff",
            edgecolor="none",
            alpha=0.5,
            zorder=0
        )
        self.ax.add_patch(patch)

        # FW square boundary
        self.ax.add_patch(
            Rectangle(
                (-half_fw, -half_fw),
                fw,
                fw,
                fill=False,
                edgecolor="#0b5ed7",
                linewidth=1.2,
                linestyle="-",
                zorder=2
            )
        )

        # OD circle boundary
        self.ax.add_patch(
            Circle(
                (0, 0),
                tip_r,
                fill=False,
                edgecolor="#6c757d",
                linewidth=1.0,
                linestyle="-",
                zorder=2
            )
        )

        # ===================================================
        # Ribs (filled + wireframe)
        # ===================================================
        for r_idx in sorted(ribs.keys()):
            sections = ribs[r_idx]
            s_ids = sorted(sections.keys())

            # --------
            # Filled rib (use outermost section)
            # --------
            outer_sid = s_ids[-1]
            pts = sections[outer_sid]
            fx = np.append(pts[:, 0], pts[0, 0])
            fy = np.append(pts[:, 1], pts[0, 1])

            self.ax.fill(
                fx,
                fy,
                facecolor="#6bcf9c",
                edgecolor="none",
                alpha=0.55,
                zorder=2
            )

            # --------
            # Internal rib structure lines
            # --------
            for i in range(len(sections[s_ids[0]])):
                lx = [sections[sid][i, 0] for sid in s_ids if i < len(sections[sid])]
                ly = [sections[sid][i, 1] for sid in s_ids if i < len(sections[sid])]
                self.ax.plot(
                    lx, ly,
                    color="#149865",
                    linewidth=0.6,
                    alpha=0.45,
                    zorder=3
                )

            # --------
            # Section outlines
            # --------
            for sid in s_ids:
                pts = sections[sid]
                sx = np.append(pts[:, 0], pts[0, 0])
                sy = np.append(pts[:, 1], pts[0, 1])

                color = "#e74c3c" if sid == s_ids[-1] else "#1f7a4a"
                lw = 1.6 if sid in (s_ids[0], s_ids[-1]) else 0.9
                alpha = 1.0 if sid in (s_ids[0], s_ids[-1]) else 0.5

                self.ax.plot(
                    sx, sy,
                    color=color,
                    linewidth=lw,
                    alpha=alpha,
                    zorder=4
                )

        # Hub
        self.ax.add_patch(
            Circle((0, 0), hub_r, facecolor="#2c3e50", alpha=0.8, zorder=10)
        )

        limit = max(tip_r, half_fw) * 1.05
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)

        self.ax.axis("off")
        self.canvas.draw()