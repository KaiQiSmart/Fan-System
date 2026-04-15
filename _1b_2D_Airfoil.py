# ==================================================
# Modified NACA 4-Digit Airfoil (Fan-oriented)
# ==================================================
# - Camber line (front / back)
# - Camber derivative
# - Modified thickness distribution
# - Upper / Lower surface construction
#
# NOTE:
# This module is a PURE algorithm module.
# No GUI, no I/O, no system calls.
# ==================================================

from math import pi, sin, cos, atan, cosh
import _1a_fan_algo_params as AP

#M=     2.1 Camber (%)
#P=     2.2 Camber Position (%)
#T=     2.3 Max Thickness (%)
#TT=    2.4 Trailing-Edge Thickness (mm)
#S=     2.9 Blade Sharpness (0~infinite)
   

#Upper Surface
#U1: Bump height (0–0.1)
#U2: Bump location along the chord (normalized, 0–1)
#U3: Bump width (0–1)

#Lower Surface
#L1: Bump height (0–0.1)
#L2: Bump location along the chord (normalized, 0–1)
#L3: Bump width (0–1)

# Bump Parameters
#U1=0.0; U2=0.0; U3=0.0   # upper-surface-bump-parameters    
#L1=0.0; L2=0.0; L3=0.0   # lower-surface-bump-parameters 



# ==================================================
# Camber Line
# ==================================================
def Ycamber_F(x, M, P):
    """Camber line (front section, x <= P)"""
    return M / P**2 * (2 * P * x - x**2)


def Ycamber_B(x, M, P):
    """Camber line (back section, x > P)"""
    return M / (1 - P)**2 * (1 + 2 * P * (x - 1) - x**2)


def Ycamber(x, M, P):
    """Unified camber line"""
    if x <= P:
        return Ycamber_F(x, M, P)
    else:
        return Ycamber_B(x, M, P)


# ==================================================
# Camber Derivative
# ==================================================
def dYcamber_F(x, M, P):
    """Camber derivative (front section)"""
    return 2 * M / P**2 * (P - x)


def dYcamber_B(x, M, P):
    """Camber derivative (back section)"""
    return 2 * M / (1 - P)**2 * (P - x)


def dYcamber(x, M, P):
    """Unified camber derivative"""
    if x <= P:
        return dYcamber_F(x, M, P)
    else:
        return dYcamber_B(x, M, P)


# ==================================================
# Thickness Distribution (Modified)
# ==================================================



def Ythickness(x, T, TT, S):
    """
    Modified thickness distribution

    T  : maximum thickness (%)
    TT : trailing-edge thickness modifier
    S  : smoothing factor
    """
    smoothing = (2 / pi * atan(S * 5 * x**2)) ** 0.25

    base_thickness = (
        T / 20
        * (AP._A0 * x**0.5 + AP._A1 * x + AP._A2 * x**2 + AP._A3 * x**3 + AP._A4 * x**4)
        + (TT / 200 * x**2)
    )

    return smoothing * base_thickness


# ==================================================
# Upper Surface
# ==================================================
def X_U(x, M, P, T, TT, S):
    return x - Ythickness(x, T, TT, S) * sin(atan(dYcamber(x, M, P))) + 1.5e-2


def Y_U(x, M, P, T, TT, S, u1, u2, u3):
    bump = u1 * (1 / cosh(x - u2)) ** ((4 / u3) ** 2)
    return (
        Ycamber(x, M, P)
        + Ythickness(x, T, TT, S) * cos(atan(dYcamber(x, M, P)))
        + 8e-2
        + bump
    )


# ==================================================
# Lower Surface
# ==================================================
def X_L(x, M, P, T, TT, S):
    return x + Ythickness(x, T, TT, S) * sin(atan(dYcamber(x, M, P))) + 1.5e-2


def Y_L(x, M, P, T, TT, S, l1, l2, l3):
    bump = l1 * (1 / cosh(x - l2)) ** ((4 / l3) ** 2)
    return (
        Ycamber(x, M, P)
        - Ythickness(x, T, TT, S) * cos(atan(dYcamber(x, M, P)))
        + 8e-2
        - bump
    )


# ==================================================
# Optional: Single-point wrapper
# ==================================================
def airfoil_point(              #ripple
    x, M, P, T, TT, S,
    u1=0.0, u2=0.0, u3=1.0,
    l1=0.0, l2=0.0, l3=1.0
):
    """
    Return upper and lower surface coordinates at x
    """
    xu = X_U(x, M, P, T, TT, S)
    yu = Y_U(x, M, P, T, TT, S, u1, u2, u3)

    xl = X_L(x, M, P, T, TT, S)
    yl = Y_L(x, M, P, T, TT, S, l1, l2, l3)

    return xu, yu, xl, yl
