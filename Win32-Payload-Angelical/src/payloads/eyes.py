# -*- coding: utf-8 -*-
"""Payload de OLHOS (tema: vigilancia sobrenatural).

EyesPayload desenha dezenas de olhos espalhados pela tela, cada um com piscar
independente, iris dourada/vermelha, pupila que acompanha o centro da tela e
veias finas na esclera. E um payload com estado (animacao frame-a-frame).
"""

import math
import random

import win32con
import win32gui

from .base import Payload


class _Olho:
    """Representa o estado de um unico olho animado."""

    # Estados da palpebra.
    ABERTO = 0
    FECHANDO = 1
    FECHADO = 2
    ABRINDO = 3

    def __init__(self, x, y, raio, cor_iris):
        self.x = x
        self.y = y
        self.raio = raio            # metade da largura do olho
        self.cor_iris = cor_iris
        self.estado = _Olho.ABERTO
        self.abertura = 1.0         # 0 (fechado) .. 1 (aberto)
        self.timer = random.randint(30, 200)   # quadros ate o proximo piscar
        self.vida = random.randint(120, 400)   # quadros ate desaparecer
        self.olhar = random.uniform(0, 2 * math.pi)

    def atualizar(self):
        """Avanca a animacao do olho em um quadro."""
        self.vida -= 1

        if self.estado == _Olho.ABERTO:
            self.timer -= 1
            if self.timer <= 0:
                self.estado = _Olho.FECHANDO
        elif self.estado == _Olho.FECHANDO:
            self.abertura -= 0.2
            if self.abertura <= 0:
                self.abertura = 0
                self.estado = _Olho.FECHADO
                self.timer = random.randint(2, 8)
        elif self.estado == _Olho.FECHADO:
            self.timer -= 1
            if self.timer <= 0:
                self.estado = _Olho.ABRINDO
        elif self.estado == _Olho.ABRINDO:
            self.abertura += 0.2
            if self.abertura >= 1:
                self.abertura = 1
                self.estado = _Olho.ABERTO
                self.timer = random.randint(40, 220)


class EyesPayload(Payload):
    """Varios olhos realistas observando, piscando de forma independente."""

    name = "Olhos Vigilantes"
    description = "Dezenas de olhos surgem e piscam observando voce."
    stateful = True

    def __init__(self, quantidade=None):
        self.quantidade = quantidade
        self.olhos = []
        self._iniciado = False

    def _cor_iris_aleatoria(self):
        """Sorteia entre iris dourada e iris vermelha."""
        if random.random() < 0.5:
            return self.rgb(255, 215, 0)     # dourado
        return self.rgb(204, 0, 0)           # vermelho

    def _novo_olho(self, w, h):
        raio = random.randint(30, 70)
        x = random.randint(raio, max(w - raio, raio + 1))
        y = random.randint(raio, max(h - raio, raio + 1))
        return _Olho(x, y, raio, self._cor_iris_aleatoria())

    def _iniciar(self, w, h):
        total = self.quantidade or random.randint(15, 25)
        for _ in range(total):
            self.olhos.append(self._novo_olho(w, h))
        self._iniciado = True

    def _desenhar_olho(self, hdc, olho, w, h):
        cx, cy = olho.x, olho.y
        rx = olho.raio               # semi-largura
        ry = int(olho.raio * 0.55)   # semi-altura (olho amendoado)

        # Altura atual da palpebra conforme a abertura.
        ry_atual = max(1, int(ry * olho.abertura))

        preto = self.rgb(0, 0, 0)

        # --- Esclera (branco do olho) em forma de amendoa via Polygon ---
        pontos_cima = []
        pontos_baixo = []
        n = 14
        for i in range(n + 1):
            t = -1 + 2 * i / n            # -1 .. 1
            px = int(cx + t * rx)
            dy = int(ry_atual * math.sqrt(max(0.0, 1 - t * t)))
            pontos_cima.append((px, cy - dy))
            pontos_baixo.append((px, cy + dy))
        contorno = pontos_cima + list(reversed(pontos_baixo))

        esclera = win32gui.CreateSolidBrush(self.rgb(245, 240, 235))
        pen_contorno = win32gui.CreatePen(win32con.PS_SOLID, 2, preto)
        old_b = win32gui.SelectObject(hdc, esclera)
        old_p = win32gui.SelectObject(hdc, pen_contorno)
        win32gui.Polygon(hdc, contorno)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(esclera)

        # Se o olho estiver quase fechado, desenha so a linha da palpebra.
        if olho.abertura < 0.15:
            win32gui.SelectObject(hdc, old_p)
            win32gui.DeleteObject(pen_contorno)
            return

        # --- Veias vermelhas finas na esclera ---
        veia_pen = win32gui.CreatePen(win32con.PS_SOLID, 1, self.rgb(200, 60, 60))
        old_vp = win32gui.SelectObject(hdc, veia_pen)
        for _ in range(4):
            ang = random.uniform(0, 2 * math.pi)
            x1 = int(cx + rx * 0.6 * math.cos(ang))
            y1 = int(cy + ry_atual * 0.6 * math.sin(ang))
            win32gui.MoveToEx(hdc, cx + random.randint(-4, 4), cy)
            win32gui.LineTo(hdc, x1, y1)
        win32gui.SelectObject(hdc, old_vp)
        win32gui.DeleteObject(veia_pen)

        # --- Iris (acompanha lentamente o centro da tela) ---
        olho.olhar += 0.02
        dir_x = (w / 2 - cx)
        dir_y = (h / 2 - cy)
        norma = math.hypot(dir_x, dir_y) or 1
        desloc = rx * 0.25
        ix = int(cx + desloc * dir_x / norma)
        iy = int(cy + desloc * dir_y / norma)
        ir = int(ry_atual * 0.9)

        iris = win32gui.CreateSolidBrush(olho.cor_iris)
        old_b = win32gui.SelectObject(hdc, iris)
        win32gui.Ellipse(hdc, ix - ir, iy - ir, ix + ir, iy + ir)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(iris)

        # --- Pupila (preta, no centro da iris) ---
        pr = max(2, int(ir * 0.45))
        pupila = win32gui.CreateSolidBrush(preto)
        old_b = win32gui.SelectObject(hdc, pupila)
        win32gui.Ellipse(hdc, ix - pr, iy - pr, ix + pr, iy + pr)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(pupila)

        # --- Brilho (ponto branco) ---
        brilho = win32gui.CreateSolidBrush(self.rgb(255, 255, 255))
        old_b = win32gui.SelectObject(hdc, brilho)
        bx = ix - pr // 2
        by = iy - pr // 2
        win32gui.Ellipse(hdc, bx, by, bx + max(2, pr // 2), by + max(2, pr // 2))
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(brilho)

        win32gui.SelectObject(hdc, old_p)
        win32gui.DeleteObject(pen_contorno)

    def draw(self, hdc, w, h):
        if not self._iniciado:
            self._iniciar(w, h)

        # Fundo preto para destacar os olhos.
        win32gui.PatBlt(hdc, 0, 0, w, h, win32con.BLACKNESS)

        sobreviventes = []
        for olho in self.olhos:
            olho.atualizar()
            self._desenhar_olho(hdc, olho, w, h)
            if olho.vida > 0:
                sobreviventes.append(olho)
            else:
                # Substitui o olho que "morreu" por um novo em outra posicao.
                sobreviventes.append(self._novo_olho(w, h))
        self.olhos = sobreviventes
