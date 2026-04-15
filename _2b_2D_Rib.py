import math

# ---------- Helper for Angle Calculation ----------
def _get_angle(v):
    return math.atan2(v[1], v[0])

# ---------- Helper for Unit Vector ----------
def _unit_vector(v):
    mag = math.sqrt(v[0]**2 + v[1]**2)
    if mag == 0: return (0,0)
    return (v[0] / mag, v[1] / mag)

# ==================================================
# MAIN GENERATOR: Trapezoidal Rib 2D
# ==================================================
def generate_rib_2d(RH, LA, TW, BW, TR, BR, steps=16):
    """
    Generates a 2D trapezoidal rib profile with fillets.
    - Top & Bottom are ALWAYS horizontal.
    - Slopes to the RIGHT (Top is shifted right relative to bottom).
    - TR: Fillet at Top-Left.
    - BR: Fillet at Bottom-Right.
    """
    
    # 1. Calculate the horizontal projection of the slope (dx)
    # LA is the angle of the left edge relative to the horizontal base.
    if 0.1 < LA < 179.9 and LA != 90:
        dx = RH / math.tan(math.radians(LA))
    else:
        dx = 0.0

    # 2. Define corners for RIGHT-leaning geometry
    # To lean RIGHT, if we set Bottom-Left at (0,0), 
    # then Top-Left must be at (dx, RH).
    
    P0 = (0.0, 0.0)              # Bottom-Left
    P1 = (dx, RH)               # Top-Left (Shifted right by dx)
    P2 = (dx + TW, RH)          # Top-Right (Horizontal top edge)
    P3 = (BW, 0.0)              # Bottom-Right (Defined by BW)

    pts = []
    TOLERANCE = 1e-4  

    def add_point(p):
        if not pts:
            pts.append(p)
        else:
            # Prevent adjacent duplicate points (Fix for CAD errors)
            dist = math.sqrt((pts[-1][0]-p[0])**2 + (pts[-1][1]-p[1])**2)
            if dist > TOLERANCE:
                pts.append(p)

    def create_fillet(p_prev, p_curr, p_next, radius):
        if radius <= 0.001:
            add_point(p_curr)
            return

        v1 = (p_prev[0]-p_curr[0], p_prev[1]-p_curr[1])
        v2 = (p_next[0]-p_curr[0], p_next[1]-p_curr[1])
        u1, u2 = _unit_vector(v1), _unit_vector(v2)
        
        dot = max(-1.0, min(1.0, u1[0]*u2[0] + u1[1]*u2[1]))
        theta = math.acos(dot)
        
        d = radius / math.tan(theta / 2.0)
        bisector = _unit_vector((u1[0]+u2[0], u1[1]+u2[1]))
        hypo = radius / math.sin(theta / 2.0)
        center = (p_curr[0] + bisector[0]*hypo, p_curr[1] + bisector[1]*hypo)
        
        t1 = (p_curr[0] + u1[0]*d, p_curr[1] + u1[1]*d)
        t2 = (p_curr[0] + u2[0]*d, p_curr[1] + u2[1]*d)
        
        a1 = _get_angle((t1[0]-center[0], t1[1]-center[1]))
        a2 = _get_angle((t2[0]-center[0], t2[1]-center[1]))
        
        diff = a2 - a1
        while diff > math.pi: diff -= 2*math.pi
        while diff < -math.pi: diff += 2*math.pi
        
        for i in range(steps + 1):
            ang = a1 + diff * (i / steps)
            add_point((center[0] + radius*math.cos(ang), center[1] + radius*math.sin(ang)))

    # --- Construct Path Sequence ---
    # Start: Bottom-Left
    add_point(P0)
    
    # 1. Top-Left Fillet (TR)
    create_fillet(P0, P1, P2, TR)
    
    # 2. Top-Right Sharp Corner
    add_point(P2)
    
    # 3. Bottom-Right Fillet (BR)
    create_fillet(P2, P3, P0, BR)
    
    return pts