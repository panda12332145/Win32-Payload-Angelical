# -*- coding: utf-8 -*-
"""OLHOS VIGILANTES — engine OpenGL.

15-25 olhos espalhados pela tela, cada um piscando de forma independente,
iris dourada/vermelha, pupila que acompanha o centro da tela, veias finas,
e leve brilho ao redor. Mesma ideia do payload GDI, mas com anti-aliasing
e mistura aditiva.
"""

import math
import random

from .base import GlEffect

GOLD = (1.0, 0.84, 0.0)
RED = (0.80, 0.05, 0.05)
WHITE = (0.97, 0.95, 0.92)


class _Olho(object):
    ABERTO = 0
    FECHANDO = 1
    FECHADO = 2
    ABRINDO = 3

    def __init__(self, w, h):
        raio = random.randint(28, 62)
        self.x = random.randint(raio + 6, max(w - raio - 6, raio + 7))
        self.y = random.randint(raio + 6, max(h - raio - 6, raio + 7))
        self.raio = raio
        self.iris = GOLD if random.random() < 0.5 else RED
        self.estado = _Olho.ABERTO
        self.abertura = 1.0
        self.timer = random.randint(35, 220)
        self.vida = random.randint(180, 520)

    def atualizar(self, dt):
        self.vida -= 1
        if self.estado == _Olho.ABERTO:
            self.timer -= 1
            if self.timer <= 0:
                self.estado = _Olho.FECHANDO
        elif self.estado == _Olho.FECHANDO:
            self.abertura -= 0.16 * dt * 60
            if self.abertura <= 0:
                self.abertura = 0
                self.estado = _Olho.FECHADO
                self.timer = random.randint(2, 9)
        elif self.estado == _Olho.FECHADO:
            self.timer -= 1
            if self.timer <= 0:
                self.estado = _Olho.ABRINDO
        elif self.estado == _Olho.ABRINDO:
            self.abertura += 0.16 * dt * 60
            if self.abertura >= 1:
                self.abertura = 1
                self.estado = _Olho.ABERTO
                self.timer = random.randint(45, 240)


class EyesGl(GlEffect):
    name = "Olhos Vigilantes"
    description = "Dezenas de olhos observando, piscando de forma independente."

    def __init__(self, quantidade=None):
        super().__init__()
        self.quantidade = quantidade
        self.olhos = []
        self.t_acumulado = 0.0

    def _novo_olho_cheio(self, w, h):
        self.olhos.append(_Olho(w, h))

    def _iniciar(self, w, h):
        total = self.quantidade or random.randint(15, 24)
        for _ in range(total):
            self._novo_olho_cheio(w, h)
        self._iniciado = True

    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        for olho in self.olhos:
            olho.atualizar(dt)
        # Substitui olhos mortos por novos (mantendo a densidade).
        self.olhos = [o for o in self.olhos if o.vida > 0]
        while len(self.olhos) < (self.quantidade or 18):
            self._novo_olho_cheio(w, h)

    def _desenhar_olho(self, r, olho, w, h, t):
        cx, cy = olho.x, olho.y
        rx = olho.raio
        ry = olho.raio * 0.56
        ry_atual = max(1.2, ry * olho.abertura)

        # Esclera amendoada (contorno)
        n = 16
        cima, baixo = [], []
        for i in range(n + 1):
            tt = -1 + 2 * i / n
            px = cx + tt * rx
            dy = ry_atual * math.sqrt(max(0.0, 1 - tt * tt))
            cima.append((px, cy - dy))
            baixo.append((px, cy + dy))
        r.poly(cima + list(reversed(baixo)), WHITE[0], WHITE[1], WHITE[2], 0.97)

        if olho.abertura < 0.15:
            r.thick_line(cx - rx * 0.85, cy, cx + rx * 0.85, cy, 2.0,
                         0.08, 0.05, 0.05, 0.95)
            return

        # Um brilho sutil atras do olho
        r.use_additive()
        r.ellipse(cx, cy, rx * 1.25, ry_atual * 1.5,
                  0.55, 0.10, 0.10, 0.10, seg=20)
        r.flush()

        # Veias (ângulos aleatórios estáveis)
        for v in range(4):
            ang = (olho.x * 0.013 + olho.y * 0.017 + v * 1.9) % (2 * math.pi)
            x1 = cx + rx * 0.75 * math.cos(ang)
            y1 = cy + ry_atual * 0.75 * math.sin(ang)
            r.thick_line(cx, cy, x1, y1, 1.2, 0.72, 0.09, 0.09, 0.5)

        # Pupila acompanha o centro da tela
        dir_x = (w / 2 - cx)
        dir_y = (h / 2 - cy)
        norma = math.hypot(dir_x, dir_y) or 1.0
        desloc = ry_atual * 0.30
        ix = cx + desloc * dir_x / norma
        iy = cy + desloc * dir_y / norma
        ir = ry_atual * 0.92

        r.ellipse(ix, iy, ir, ir, olho.iris[0], olho.iris[1], olho.iris[2], 0.96, seg=18)
        r.ring_ellipse(ix, iy, ir, ir, ir * 0.88, ir * 0.82,
                       0.30, 0.18, 0.08, 0.75, seg=18)
        pr = max(2.2, ir * 0.46)
        r.ellipse(ix, iy, pr, pr, 0.02, 0.02, 0.02, 1.0, seg=12)
        r.ellipse(ix - pr * 0.4, iy - pr * 0.4, max(1.5, pr * 0.30), max(1.5, pr * 0.30),
                   1.0, 1.0, 1.0, 0.9, seg=8)

    def draw(self, r, w, h, t):
        r.clear(0.015, 0.010, 0.012, 1.0)
        for olho in self.olhos:
            self._desenhar_olho(r, olho, w, h, t)
