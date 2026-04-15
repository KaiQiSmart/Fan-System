# ==================================================
# _1c_3D_Blade.py
# 3D mapping based on 2D airfoil from _1b_2D_Airfoil.py
# ==================================================
# PURE algorithm module
# - No GUI
# - No I/O
# - No system calls
# ==================================================

from math import pi, sin, cos, asin, acos, tan, atan

import _1b_2D_Airfoil as A

#M=     2.1 Camber (%)
#P=     2.2 Camber Position (%)
#T=     2.3 Max Thickness (%)
#TT=    2.4 Trailing-Edge Thickness (mm)
#S=     2.9 Blade Sharpness (0~infinite)
#Aoi=   2.5 Angle of Incidence (deg)
#L=     2.6 Leading Edge Offset (mm)
#H=     2.7 Height (mm)
#F=     2.8 F-angle (deg)

# Computational Parameter
# Fold : Accumulated forward sweep angle (rad), state variable
# D    : Current section diameter (mm)
# D0   : Previous section diameter (mm), used for incremental sweep calculation
# Note :
#   For i = 0 (root section):
#   D  = ID
#   D0 = 0.0   # initialization only, not a physical diameter

   
#Upper Surface
#U1: Bump height (0–0.1)
#U2: Bump location along the chord (normalized, 0–1)
#U3: Bump width (0–1)

#Lower Surface
#L1: Bump height (0–0.1)
#L2: Bump location along the chord (normalized, 0–1)
#L3: Bump width (0–1)

# ==================================================
# R = sqrt(x^2 + y^2)
# ==================================================
def disRU(x, M, P, T, TT, S, u1, u2, u3):
    xu = A.X_U(x, M, P, T, TT, S)
    yu = A.Y_U(x, M, P, T, TT, S, u1, u2, u3)
    return (xu * xu + yu * yu) ** 0.5


def disRL(x, M, P, T, TT, S, l1, l2, l3):
    xl = A.X_L(x, M, P, T, TT, S)
    yl = A.Y_L(x, M, P, T, TT, S, l1, l2, l3)
    return (xl * xl + yl * yl) ** 0.5


# ==================================================
# (X1, Y1): transform in 2D reference frame
# ==================================================
def X_1_U(x, M, P, T, TT, Aoi, S, u1, u2, u3):
    xu = A.X_U(x, M, P, T, TT, S)
    yu = A.Y_U(x, M, P, T, TT, S, u1, u2, u3)
    r = disRU(x, M, P, T, TT, S, u1, u2, u3)

    xu0 = A.X_U(0.0, M, P, T, TT, S)
    yu0 = A.Y_U(0.0, M, P, T, TT, S, u1, u2, u3)
    r0 = (xu0 * xu0 + yu0 * yu0) ** 0.5

    return r * cos(-Aoi * pi / 180 + acos(xu / r)) - r0 * cos(-Aoi * pi / 180 + acos(xu0 / r0))


def Y_1_U(x, M, P, T, TT, Aoi, S, u1, u2, u3):
    xu = A.X_U(x, M, P, T, TT, S)
    yu = A.Y_U(x, M, P, T, TT, S, u1, u2, u3)
    r = disRU(x, M, P, T, TT, S, u1, u2, u3)

    xu0 = A.X_U(0.0, M, P, T, TT, S)
    yu0 = A.Y_U(0.0, M, P, T, TT, S, u1, u2, u3)
    r0 = (xu0 * xu0 + yu0 * yu0) ** 0.5

    return r * sin(-Aoi * pi / 180 + asin(yu / r)) - r0 * sin(-Aoi * pi / 180 + asin(yu0 / r0))


def X_1_L(x, M, P, T, TT, Aoi, S, l1, l2, l3):
    xl = A.X_L(x, M, P, T, TT, S)
    yl = A.Y_L(x, M, P, T, TT, S, l1, l2, l3)
    r = disRL(x, M, P, T, TT, S, l1, l2, l3)

    xl0 = A.X_L(0.0, M, P, T, TT, S)
    yl0 = A.Y_L(0.0, M, P, T, TT, S, l1, l2, l3)
    r0 = (xl0 * xl0 + yl0 * yl0) ** 0.5

    return r * cos(-Aoi * pi / 180 + acos(xl / r)) - r0 * cos(-Aoi * pi / 180 + acos(xl0 / r0))


def Y_1_L(x, M, P, T, TT, Aoi, S, l1, l2, l3):
    xl = A.X_L(x, M, P, T, TT, S)
    yl = A.Y_L(x, M, P, T, TT, S, l1, l2, l3)
    r = disRL(x, M, P, T, TT, S, l1, l2, l3)

    xl0 = A.X_L(0.0, M, P, T, TT, S)
    yl0 = A.Y_L(0.0, M, P, T, TT, S, l1, l2, l3)
    r0 = (xl0 * xl0 + yl0 * yl0) ** 0.5

    return r * sin(-Aoi * pi / 180 + asin(yl / r)) - r0 * sin(-Aoi * pi / 180 + asin(yl0 / r0))


# ==================================================
# AOI weighting & F-angle transform
# ==================================================
def Aoi_weigh(D, Aoi, H):
    chord_act = H * (1.0 / sin(Aoi * pi / 180))
    return chord_act / (D / 2.0)


def Fang_transf(D, F, D0):
    return atan((1.0 - D0 / D) * tan(F * pi / 180))


# ==================================================
# (X2, Y2, Z2): 3D mapping to cylindrical blade surface
# ==================================================
def X_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, u1, u2, u3):
    ang = Aoi_weigh(D, Aoi, H) * X_1_U(x, M, P, T, TT, Aoi, S, u1, u2, u3) - Fang_transf(D, F, D0) - Fold
    return (D / 2.0) * sin(ang)


def Y_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, u1, u2, u3):
    ang = Aoi_weigh(D, Aoi, H) * X_1_U(x, M, P, T, TT, Aoi, S, u1, u2, u3) - Fang_transf(D, F, D0) - Fold
    return (D / 2.0) * cos(ang)


def Z_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, S, u1, u2, u3):
    return (D / 2.0) * Aoi_weigh(D, Aoi, H) * Y_1_U(x, M, P, T, TT, Aoi, S, u1, u2, u3) + L


def X_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, l1, l2, l3):
    ang = Aoi_weigh(D, Aoi, H) * X_1_L(x, M, P, T, TT, Aoi, S, l1, l2, l3) - Fang_transf(D, F, D0) - Fold
    return (D / 2.0) * sin(ang)


def Y_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, l1, l2, l3):
    ang = Aoi_weigh(D, Aoi, H) * X_1_L(x, M, P, T, TT, Aoi, S, l1, l2, l3) - Fang_transf(D, F, D0) - Fold
    return (D / 2.0) * cos(ang)


def Z_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, S, l1, l2, l3):
    return (D / 2.0) * Aoi_weigh(D, Aoi, H) * Y_1_L(x, M, P, T, TT, Aoi, S, l1, l2, l3) + L


# ==================================================
# Convenience wrappers
# ==================================================
def blade_point_upper(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, u1, u2, u3):
    return (
        X_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, u1, u2, u3),
        Y_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, u1, u2, u3),
        Z_2_U(x, M, P, T, TT, D, Aoi, L, H, F, D0, S, u1, u2, u3),
    )


def blade_point_lower(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, l1, l2, l3):
    return (
        X_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, l1, l2, l3),
        Y_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, Fold, S, l1, l2, l3),
        Z_2_L(x, M, P, T, TT, D, Aoi, L, H, F, D0, S, l1, l2, l3),
    )
