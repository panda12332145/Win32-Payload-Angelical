# -*- coding: utf-8 -*-
"""Matematica 3D compartilhada pelos efeitos OpenGL.

Mesma tecnica usada pelo payload GDI original (rotacao 3D + projecao em
perspectiva), mas isolada aqui para ser reutilizada sem dependencias de
GDI/pywin32.
"""

import math


def rot(i, j, k, A, B, C):
    """Rotaciona o ponto (i, j, k) pelos angulos A, B, C."""
    x = (j * math.sin(A) * math.sin(B) * math.cos(C)
         - k * math.cos(A) * math.sin(B) * math.cos(C)
         + j * math.cos(A) * math.sin(C)
         + k * math.sin(A) * math.sin(C)
         + i * math.cos(B) * math.cos(C))
    y = (j * math.cos(A) * math.cos(C)
         + k * math.sin(A) * math.cos(C)
         - j * math.sin(A) * math.sin(B) * math.sin(C)
         + k * math.cos(A) * math.sin(B) * math.sin(C)
         - i * math.cos(B) * math.sin(C))
    z = (k * math.cos(A) * math.cos(B)
         - j * math.sin(A) * math.cos(B)
         + i * math.sin(B))
    return x, y, z


def project(x, y, z, cx, cy, focal, dist):
    """Projecao em perspectiva. Retorna (xp, yp, escala).

    escala ~ focal / (z + dist); quanto maior a escala, mais perto do "olho".
    """
    z = z + dist
    if z <= 1.0:
        z = 1.0
    ooz = 1.0 / z
    xp = cx + focal * ooz * x
    yp = cy - focal * ooz * y
    escala = focal * ooz
    return xp, yp, escala
