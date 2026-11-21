# -*- coding: utf-8 -*-
"""GLITCH DIGITAL — engine OpenGL.

Blocos de cor aleatorios com cortes horizontais e offset de tela, simulando
corrupcao de video. Contrastes fortes (vermelho/ciano) + ruido.
"""

import math
import random

from .base import GlEffect


class GlitchGl(GlEffect):
    name = "Glitch Digital"
    description = "Blocos coloridos aleatorios simulando corrupcao de video."

    def __init__(self):
        super().__init__()
        self.seed = random.random() * 100.0
        self.t_acumulado = 0.0

    def update(self, dt, w, h, t):
        self.t_acumulado += dt

    def draw(self, r, w, h, t):
        r.clear(0.06, 0.06, 0.07, 1.0)

        # Streaks horizontais aleatorios
        for _ in range(38):
            y = random.randint(0, max(h - 1, 0))
            bh = random.randint(3, 64)
            x = random.randint(-120, w)
            bw = random.randint(40, 1000)
            escolha = random.random()
            if escolha < 0.22:
                col = (1.00, 0.08, 0.08)
            elif escolha < 0.44:
                col = (0.10, 0.90, 1.00)
            elif escolha < 0.58:
                col = (1.00, 0.90, 0.08)
            elif escolha < 0.78:
                col = (0.05, 0.05, 0.05)
            else:
                col = (random.random() * 0.9 + 0.05,
                       random.random() * 0.9 + 0.05,
                       random.random() * 0.9 + 0.05)
            alpha = 0.55 + random.random() * 0.40
            r.rect(x, y, bw, bh, col[0], col[1], col[2], alpha)

        # Jitter de "linha" inteira (uma vez por frame)
        if random.random() < 0.55:
            y = random.randint(0, max(h - 8, 0))
            bh = random.randint(8, 48)
            offset = random.randint(-60, 60)
            r.rect(offset, y, w, bh,
                   1.0 if random.random() < 0.5 else 0.08,
                   0.08 if random.random() < 0.5 else 0.90,
                   1.0, 0.75)

        # Ruido granular disperso
        for _ in range(80):
            x = random.randint(0, w)
            y = random.randint(0, h)
            bw = random.randint(2, 10)
            col = random.choice([(1.0, 1.0, 1.0), (0.0, 0.0, 0.0),
                                 (0.0, 1.0, 1.0), (1.0, 0.05, 0.05)])
            r.rect(x, y, bw, bw, col[0], col[1], col[2], 0.50)

        # "Cor" da tela substituida por flicker ocasional
        if random.random() < 0.14:
            r.rect(0, 0, w, h, 1.0, 1.0, 1.0, 0.22)
        elif random.random() < 0.10:
            y = random.randint(0, max(h - 30, 0))
            r.rect(0, y, w, random.randint(4, 12), 0.0, 1.0, 0.9, 0.85)
