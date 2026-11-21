# -*- coding: utf-8 -*-
"""CRANIOS — engine OpenGL.

Cranios fantasmagoricos desenhados com primitivas para anti-aliasing: cranio
elixado com borda, mandibula, orbitas oculares, nariz, dentes, halo
avermelhado sutil ao redor.
"""

import math
import random

from .base import GlEffect


class SkullGl(GlEffect):
    name = "Cranios"
    description = "Cranios fantasmagoricos desenhados em OpenGL."

    def __init__(self):
        super().__init__()
        self.cranios = []
        self._w = 0
        self._h = 0

    def _novo_cranio(self, w, h):
        tam = random.randint(90, 230)
        return {
            "x": random.randint(tam, max(w - tam, tam + 1)),
            "y": random.randint(tam, max(h - tam, tam + 1)),
            "tam": tam,
            "tilt": random.uniform(-0.22, 0.22),
        }

    def _iniciar(self, w, h):
        self.cranios = []
        for _ in range(8):
            self.cranios.append(self._novo_cranio(w, h))
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)

    def draw(self, r, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        r.clear(0.02, 0.018, 0.024, 1.0)

        for c in self.cranios:
            # Halo sutil
            r.use_additive()
            r.ellipse(c["x"], c["y"], c["tam"] * 0.95, c["tam"] * 0.92,
                      0.30, 0.04, 0.05, 0.28, seg=24)
            r.flush()

            # Balanço sutil de tilt via rotação visual não suportada -> desenha
            # na orientação natural (precondição de simplicidade).
            self._draw_cranio(r, c["x"], c["y"], c["tam"])

    def _draw_cranio(self, r, cx, cy, tam):
        branco = (0.93, 0.92, 0.86)
        borda = (0.06, 0.05, 0.05)

        # Cranio (elipse superior)
        r.ellipse(cx, cy - tam * 0.05, tam * 0.46, tam * 0.44,
                  branco[0], branco[1], branco[2], 0.98, seg=32)

        # Mandíbula (trapezoid via retângulo arredondado aproximado com ellipse
        # pequeno)
        r.ellipse(cx, cy + tam * 0.30, tam * 0.24, tam * 0.26,
                  branco[0] * 0.97, branco[1] * 0.97, branco[2] * 0.97, 0.98, seg=20)

        # Borda do crânio (contorno)
        r.ring_ellipse(cx, cy - tam * 0.05, tam * 0.46, tam * 0.44,
                       tam * 0.44, tam * 0.42,
                       borda[0], borda[1], borda[2], 0.70, seg=32)

        # Orbitas oculares
        orbita_w = tam * 0.155
        orbita_h = tam * 0.20
        oy = cy - tam * 0.10
        for lado in (-1, +1):
            ex = cx + lado * tam * 0.24
            r.ellipse(ex, oy, orbita_w, orbita_h, 0.03, 0.02, 0.02, 1.0, seg=14)
            # Brilho interno vermelho (orbe sombrio)
            r.ellipse(ex, oy, orbita_w * 0.36, orbita_h * 0.36,
                      0.55, 0.05, 0.05, 0.85, seg=8)

        # Nariz (triângulo preto)
        r.poly([(cx, cy + tam * 0.02),
                (cx - tam * 0.09, cy + tam * 0.15),
                (cx + tam * 0.09, cy + tam * 0.15)],
               0.03, 0.02, 0.02, 1.0)

        # Dentes
        dente_y = cy + tam * 0.22
        dente_h = tam * 0.09
        dente_w = tam * 0.075
        for i in range(4):
            dx = cx - tam * 0.24 + i * dente_w * 1.28
            r.rect(dx, dente_y, dente_w * 0.78, dente_h,
                   branco[0] * 0.96, branco[1] * 0.96, branco[2] * 0.96, 0.95)
            r.rect(dx, dente_y + dente_h, dente_w * 0.78, 1.8,
                   borda[0], borda[1], borda[2], 0.90)
