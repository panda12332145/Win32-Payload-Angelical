# -*- coding: utf-8 -*-
"""ESCURIDAO — engine OpenGL.

Vinheta de escuridao pulsante com estrelas distantes. Ramificados de anéis
com alpha suave + mais um centro claro pulsante. Fundo quase negro.
"""

import math
import random

from .base import GlEffect


class DarknessGl(GlEffect):
    name = "Escuridao"
    description = "Trevas pulsantes consumindo a tela, com estrelas distantes."

    def __init__(self):
        super().__init__()
        self.fase = 0.0
        self.estrelas = []
        self._iniciado = False

    def _iniciar(self, w, h):
        for _ in range(150):
            self.estrelas.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "tam": random.uniform(0.6, 2.4),
                "fase": random.uniform(0, 2 * math.pi),
                "freq": random.uniform(0.6, 2.4),
            })
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        self.fase += dt * 1.4

    def draw(self, r, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        pulso = (math.sin(self.fase) + 1.0) / 2.0

        # Fundo: "céu" escurecido (vinheta fica sobre ele)
        r.clear(0.085, 0.050, 0.032, 1.0)

        # Estrelas (antes da vinheta)
        for est in self.estrelas:
            brilho = 0.55 + 0.45 * math.sin(t * est["freq"] + est["fase"])
            r.point(est["x"], est["y"], est["tam"],
                    brilho, brilho, brilho * 1.05, max(0.0, brilho * 0.9))

        # Vinheta: elipses concentricas escurecendo das bordas para o centro
        cx, cy = w * 0.5, h * 0.5
        max_r = math.hypot(w, h) / 2.0

        n_aneis = 34
        for i in range(n_aneis, 0, -1):
            frac = i / n_aneis
            r_anel = max_r * frac
            opacidade = (frac ** 1.55) * 0.80
            if opacidade <= 0.01:
                continue
            r.ellipse(cx, cy, r_anel, r_anel, 0.0, 0.0, 0.012, opacidade, seg=48)

        # Círculo central claro (o "olho das trevas")
        r.use_additive()
        raio_luz = max_r * (0.05 + pulso * 0.045)
        for i in range(6, 0, -1):
            frac = i / 6.0
            rr = raio_luz * (1.7 + frac * 2.4)
            r.ellipse(cx, cy, rr, rr * 0.86,
                      0.34, 0.07, 0.03, 0.12 * (1 - frac), seg=40)
        r.flush()
