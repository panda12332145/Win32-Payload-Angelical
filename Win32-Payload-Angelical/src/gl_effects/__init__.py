# -*- coding: utf-8 -*-
"""Pacote de efeitos OpenGL (3D) do Win32-Payload-Angelical.

Cada efeito combina geometria triangulada + shaders pequenos via OpenGL
(PyOpenGL), com blending e anti-aliasing — substituicoes de qualidade para os
payloads GDI originais (que desenham com primitivas 2D sem suavizacao).
"""

from .base import GlEffect
from .angel import OphanimAngelGl
from .eyes import EyesGl
from .blood import BloodDropGl
from .cracks import CracksGl
from .darkness import DarknessGl
from .shadow import ShadowFigureGl
from .glitch import GlitchGl
from .skulls import SkullGl

# Registro de todos os efeitos OpenGL (ordem do menu).
GL_EFFECTS = [
    OphanimAngelGl,
    EyesGl,
    BloodDropGl,
    CracksGl,
    ShadowFigureGl,
    SkullGl,
    DarknessGl,
    GlitchGl,
]

__all__ = [
    "GlEffect",
    "OphanimAngelGl",
    "EyesGl",
    "BloodDropGl",
    "CracksGl",
    "ShadowFigureGl",
    "SkullGl",
    "DarknessGl",
    "GlitchGl",
    "GL_EFFECTS",
]
