# -*- coding: utf-8 -*-
"""SANGUE ESCORRENDO — engine OpenGL.

Gotas de sangue caindo com gravidade, se acumulam no fundo da tela
(poca crescente), borda escura no topo. dt-based, anti-aliased.
"""

import math
import random

from .base import GlEffect


class BloodDropGl(GlEffect):
    name = "Sangue Escorrendo"
    description = "Gotas de sangue caem, aceleram e se acumulam no fundo."

    def __init__(self):
        super().__init__()
        self.gotas = []
        self.poca = {}  # coluna (x//12) -> altura acumulada
        self._w = 0
        self._h = 0

    def _nova_gota(self, w, h, topo=False):
        return {
            "x": random.uniform(0, w),
            "y": (random.uniform(-h, 0) if topo else random.uniform(-220, -20)),
            "vy": random.uniform(90, 260),
            "comprimento": random.uniform(22, 95),
            "largura": random.uniform(3, 7),
            "cor": random.choice([(0.55, 0.02, 0.04), (0.62, 0.03, 0.05)]),
        }

    def _iniciar(self, w, h):
        for _ in range(64):
            self.gotas.append(self._nova_gota(w, h, topo=True))
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        self._w, self._h = w, h
        for gota in self.gotas:
            gota["vy"] += 340.0 * dt           # gravidade (px/s^2)
            gota["y"] += gota["vy"] * dt
            col = int(gota["x"] // 12)
            altura_poca = self.poca.get(col, 0.0)
            limite = h - altura_poca
            if gota["y"] + gota["comprimento"] >= limite:
                self.poca[col] = min(altura_poca + gota["comprimento"] * 0.16, h * 0.42)
                novo = self._nova_gota(w, h)
                gota.update(novo)

    def draw(self, r, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        r.clear(0.02, 0.015, 0.018, 1.0)

        # Cauda escura no topo (ar de fundo escurecido)
        for i in range(6):
            y0 = i * (h * 0.028)
            r.rect(0, y0, w, h * 0.028, 0.10, 0.02, 0.02, 0.18 * (1 - i / 6))

        # Poca acumulada (borda levemente mais clara em cima)
        for col, altura in self.poca.items():
            if altura <= 0.5:
                continue
            x0 = col * 12
            r.rect(x0, h - altura, 12, altura + 1, 0.34, 0.02, 0.03, 0.95)
            r.rect(x0, h - altura, 12, max(2.5, altura * 0.18), 0.55, 0.06, 0.06, 0.95)

        # Gotas
        for gota in self.gotas:
            x = int(gota["x"])
            y = int(gota["y"])
            comp = gota["comprimento"]
            larg = gota["largura"]
            r.rect(x, y, larg, comp, gota["cor"][0], gota["cor"][1], gota["cor"][2], 0.95)
            r.ellipse(x + larg * 0.5, y + comp, larg * 0.85, max(3.0, larg * 0.8),
                      0.72, 0.05, 0.05, 0.95, seg=10)
            # toques de brilho
            r.ellipse(x + larg * 0.35, y + comp * 0.35, larg * 0.35, comp * 0.22,
                      0.85, 0.14, 0.14, 0.45, seg=8)
