# -*- coding: utf-8 -*-
"""FIGURA SOMBRIA — engine OpenGL.

Silhueta humanoide escura que aparece e desaparece em fade, com olhos vermelhos
brilhantes quando a figura está mais visível. Fundo quase negro com poeira
lenta. Fade via senoidal (estado em dt-based).
"""

import math
import random

from .base import GlEffect


class ShadowFigureGl(GlEffect):
    name = "Figura Sombria"
    description = "Uma silhueta humanoide surge lentamente das trevas."

    def __init__(self):
        super().__init__()
        self.fase = 0.0
        self.base_x = None
        self.dust = []

    def _iniciar(self, w, h):
        self.base_x = w // 2
        for _ in range(50):
            self.dust.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "vy": random.uniform(4, 14),
                "tam": random.uniform(1.0, 2.6),
                "fase": random.uniform(0, 2 * math.pi),
            })
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        self.fase += dt * 0.9
        intensidade = (math.sin(self.fase) + 1) / 2.0
        if intensidade < 0.04:
            self.base_x = random.randint(int(w * 0.22), int(w * 0.78))

        for p in self.dust:
            p["y"] -= p["vy"] * dt
            if p["y"] < -5:
                p["y"] = h + 5
                p["x"] = random.uniform(0, w)

    def draw(self, r, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        r.clear(0.012, 0.010, 0.013, 1.0)

        intensidade = (math.sin(self.fase) + 1) / 2.0
        if intensidade < 0.02:
            intensidade = 0.02

        # Poeira lenta
        for p in self.dust:
            brilho = 0.10 + 0.10 * math.sin(t * 1.2 + p["fase"])
            r.point(p["x"], p["y"], p["tam"], 0.5, 0.5, 0.5, max(0.0, brilho))

        cx = self.base_x
        topo = int(h * 0.26)
        escala = h * 0.46

        # Halo avermelhado sutil atrás da figura
        r.use_additive()
        r.ellipse(cx, topo + escala * 0.35, escala * 0.55, escala * 0.62,
                  0.35, 0.04, 0.03, 0.20 * intensidade, seg=32)
        r.flush()

        # Borda escura da silhueta (rgba com variações suaves)
        tom = 0.06 + intensidade * 0.16
        cor = (tom, tom, tom * 1.15)
        alpha = 0.55 + 0.45 * intensidade

        cabeca_r = int(escala * 0.095)

        # Cabeca
        r.ellipse(cx, topo + cabeca_r, cabeca_r, cabeca_r, cor[0], cor[1], cor[2], alpha, seg=26)

        # Ombros + tronco (poligono trapezoidal)
        ombro_y = topo + cabeca_r * 2
        quadril_y = int(topo + escala * 0.84)
        tronco = [
            (cx - int(escala * 0.15), ombro_y),
            (cx + int(escala * 0.15), ombro_y),
            (cx + int(escala * 0.105), quadril_y),
            (cx - int(escala * 0.105), quadril_y),
        ]
        r.poly(tronco, cor[0], cor[1], cor[2], alpha)

        # Bracos
        larg_braco = max(4.0, escala * 0.045)
        r.thick_line(cx - int(escala * 0.13), ombro_y + 6, cx - int(escala * 0.21), quadril_y,
                     larg_braco, cor[0], cor[1], cor[2], alpha)
        r.thick_line(cx + int(escala * 0.13), ombro_y + 6, cx + int(escala * 0.21), quadril_y,
                     larg_braco, cor[0], cor[1], cor[2], alpha)

        # Pés/pernas (trapezoidais)
        perna_tam = int(escala * 0.075)
        pele_y_base = quadril_y
        pele_y_base_final = int(topo + escala * 1.05)
        for lado in (-1, +1):
            perna = [
                (cx + lado * int(escala * 0.105) - perna_tam // 2, pele_y_base),
                (cx + lado * int(escala * 0.105) + perna_tam // 2, pele_y_base),
                (cx + lado * int(escala * 0.115) + perna_tam // 2, pele_y_base_final),
                (cx + lado * int(escala * 0.115) - perna_tam // 2, pele_y_base_final),
            ]
            r.poly(perna, cor[0] * 0.85, cor[1] * 0.85, cor[2] * 0.85, alpha * 0.95)

        # Olhos vermelhos brilhantes (quando mais visivel)
        if intensidade > 0.35:
            brilho = (intensidade - 0.35) / 0.65
            olho_y = topo + cabeca_r - 2
            raio_ol = max(2.5, cabeca_r * 0.22)
            r.use_additive()
            for lado in (-1, +1):
                ex = cx + lado * cabeca_r * 0.42
                r.ellipse(ex, olho_y, raio_ol, raio_ol * 0.8,
                          1.00, 0.05, 0.05, 0.75 * brilho, seg=10)
            r.flush()
