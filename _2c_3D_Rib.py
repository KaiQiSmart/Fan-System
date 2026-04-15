# ================================================================================
# PROJECT: Fan Integrated Design Platform
# MODULE: _2c_3D_Rib.py
# DESCRIPTION: 
#   2D to 3D cylindrical mapping with Rake Angle (Vertical Lift)
# ==================================================
import math
import _2a_rib_algo_params as AP

def get_section_params(t):
    """
    Interpolates rib parameters from Root (t=0) to Tip (t=1).
    t: normalized spanwise position [0.0, 1.0]
    """
    # 1. Current Radius calculation
    r_root = AP.ID / 2.0
    r_tip = AP.OD / 2.0
    current_r = r_root + t * (r_tip - r_root)

    # 2. Rake Angle Calculation (Vertical Lift)
    # Rake is defined as the angle relative to the horizontal plane.
    # The height (Z) increases as the radius increases.
    # Z = Delta_R * tan(Rake_Angle)
    rake_rad = math.radians(AP.RAKE)
    delta_r = current_r - r_root
    z_lift = delta_r * math.tan(rake_rad)

    return {
        # Geometry interpolation
        "RH": AP.R_RH + (AP.T_RH - AP.R_RH) * t,
        "LA": AP.R_LA + (AP.T_LA - AP.R_LA) * t,
        "TW": AP.R_TW + (AP.T_TW - AP.R_TW) * t,
        "BW": AP.R_BW + (AP.T_BW - AP.R_BW) * t,
        "TR": AP.R_TR + (AP.T_TR - AP.R_TR) * t,
        "BR": AP.R_BR + (AP.T_BR - AP.R_BR) * t,
        
        # Cylindrical mapping parameters
        "R": current_r,
        "FA": math.radians(AP.FA * t),   # Flare Angle (Circumferential rotation)
        "Z_offset": z_lift,               # Rake Angle effect (Vertical lift)
    }

def map_2d_to_3d(pts_2d, R, FA, Z_offset):
    """
    Maps 2D trapezoidal points onto a 3D cylindrical surface.
    - 2D X -> Wrapped around cylinder circumference (Theta)
    - 2D Y -> Cylinder height (Z)
    """
    pts_3d = []
    
    # Tolerance for CAD kernel stability (points too close)
    TOLERANCE = 1e-4 

    for px, py in pts_2d:
        # 1. Calculate Angular position (theta)
        # s = r * theta  =>  theta = s / r
        theta = FA + (px / R)
        
        # 2. Polar to Cartesian conversion
        x = R * math.cos(theta)
        y = R * math.sin(theta)
        
        # 3. Height mapping
        # Z = base lift from Rake + the 2D height of the rib itself
        z = Z_offset + py
        
        # 4. Duplicate/Close Point Filtering
        if not pts_3d:
            pts_3d.append((x, y, z))
        else:
            last_p = pts_3d[-1]
            dist = math.sqrt((x - last_p[0])**2 + (y - last_p[1])**2 + (z - last_p[2])**2)
            
            if dist > TOLERANCE:
                pts_3d.append((x, y, z))
                
    return pts_3d

if __name__ == "__main__":
    # Example: 10 degree rake angle lift test
    # AP.RAKE = 10.0, AP.ID = 30.0, AP.OD = 90.0
    # At Tip (t=1): Delta_R = 30, Z_lift = 30 * tan(10deg) approx 5.28mm
    p = get_section_params(1.0)
    print(f"Tip Radius: {p['R']}, Tip Z-Lift (Rake Angle Effect): {p['Z_offset']:.4f} mm")