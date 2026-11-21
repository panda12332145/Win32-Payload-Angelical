# -*- coding: utf-8 -*-
"""RACHADURAS — engine OpenGL.

Rachaduras se espalhando recursivamente a partir de pontos da tela. Cada
ponto ramifica com probabilidade, criando atritos destrutivos. Borda branca
espessada + nucleo preto + leve halo avermelhado.
"""

import math
import random

from .base import GlEffect


class CracksGl(GlEffect):
    name = "Rachaduras"
    description = "Rachaduras negras se espalhando pela tela."

    def __init__(self):
        super().__init__()
        self.pontas = []
        self.segmentos = []
        self._w = 0
        self._h = 0

    def _iniciar(self, w, h):
        self.segmentos = []
        self.pontas = []
        for _ in range(4):
            self.pontas.append({
                "x": random.randint(int(w * 0.15), int(w * 0.85)),
                "y": random.randint(int(h * 0.15), int(h * 0.85)),
                "ang": random.uniform(0, 2 * math.pi),
                "vida": random.randint(50, 110),
            })
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        passo_base = 340.0 * dt
        novas = []
        for ponta in self.pontas:
            if ponta["vida"] <= 0:
                continue
            ponta["ang"] += random.uniform(-0.45, 0.45)
            passo = random.uniform(220, 620) * dt + passo_base * 0.5
            nx = ponta["x"] + passo * math.cos(ponta["ang"])
            ny = ponta["y"] + passo * math.sin(ponta["ang"])
            self.segmentos.append((ponta["x"], ponta["y"], nx, ny))
            ponta["x"], ponta["y"] = nx, ny
            ponta["vida"] -= 1
            if random.random() < 0.075 and len(self.pontas) + len(novas) < 44:
                novas.append({
                    "x": nx, "y": ny,
                    "ang": ponta["ang"] + random.uniform(-1.4, 1.4),
                    "vida": ponta["vida"] // 2,
                })
            if 0 <= nx <= w and 0 <= ny <= h:
                novas.append(ponta)
        self.pontas = novas
        if not self.pontas:
            self._iniciar(w, h)

    def draw(self, r, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        r.clear(0.06, 0.055, 0.06, 1.0)

        # Vinheta suave
        r.use_additive()
        for i in range(8, 0, -1):
            frac = i / 8.0
            rr = max(w, h) * 0.62 * frac
            r.ellipse(w * 0.5, h * 0.5, rr, rr * 0.78,
                      0.10, 0.02, 0.03, 0.09 * (1 - frac), seg=28)
        r.flush()

        for (x1, y1, x2, y2) in self.segmentos:
            r.thick_line(x1, y1, x2, y2, 7.0, 0.88, 0.88, 0.86, 0.92)
        for (x1, y1, x2, y2) in self.segmentos:
            r.thick_line(x1, y1, x2, y2, 2.6, 0.02, 0.02, 0.02, 0.98)
