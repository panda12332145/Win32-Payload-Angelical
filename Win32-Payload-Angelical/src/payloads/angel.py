# -*- coding: utf-8 -*-
"""Payload principal: ANJO TRONO (OPHANIM) animado em GDI.

Baseado na descricao biblica dos Tronos / Ophanim (Ezequiel 1 e 10):
rodas dentro de rodas, cobertas de olhos, com asas e fogo.

O OphanimAngelPayload e um payload COM ESTADO (stateful): cada chamada a
``draw()`` avanca um quadro da animacao. Os aneis giram em velocidades e
direcoes diferentes usando rotacao 3D com projecao em perspectiva (mesma
tecnica do IconCubePayload original), o olho central pisca, as asas batem
em onda senoidal, particulas de fogo sobem e o brilho dourado/vermelho pulsa.

Cores do tema:
    Dourado        RGB(255, 215, 0)
    Vermelho vivo  RGB(220, 20, 60)
    Vermelho-sangue RGB(139, 0, 0)
    Laranja fogo   RGB(255, 69, 0)
    Branco         RGB(255, 255, 255)
    Preto          RGB(0, 0, 0)
"""

import math
import random

import win32con
import win32gui

from .base import Payload
from .fonts import criar_fonte


class OphanimAngelPayload(Payload):
    """Anjo Trono biblico completo e animado desenhado inteiramente em GDI."""

    name = "Anjo Trono (Ophanim)"
    description = ("Anjo biblico Trono: aneis girando com olhos, olho central "
                   "piscando, asas batendo, fogo e brilho dourado.")
    stateful = True

    # Paleta de cores (preenchida em _init_cores pois usa win32api.RGB).
    def __init__(self):
        self.ring_angles = [0.0, 0.0, 0.0]      # angulo de rotacao de cada anel
        self.ring_speeds = [0.04, -0.03, 0.02]  # velocidade/direcao de cada anel
        self.ring_tilts = [0.0, 0.0, 0.0]       # inclinacao 3D de cada anel
        self.eye_blink = 0.0                     # fase do piscar do olho central
        self.wing_phase = 0.0                    # fase do batimento das asas
        self.glow_pulse = 0.0                    # fase do pulso de brilho
        self.fire_particles = []                 # particulas de fogo
        self.frame = 0
        self._iniciado = False

        # Cores do tema.
        self.DOURADO = self.rgb(255, 215, 0)
        self.DOURADO_ESC = self.rgb(180, 140, 0)
        self.VERMELHO = self.rgb(220, 20, 60)
        self.SANGUE = self.rgb(139, 0, 0)
        self.FOGO = self.rgb(255, 69, 0)
        self.BRANCO = self.rgb(255, 255, 255)
        self.PRETO = self.rgb(0, 0, 0)

    # ------------------------------------------------------------------ #
    # Rotacao 3D (A, B, C) + projecao em perspectiva.
    # ------------------------------------------------------------------ #
    @staticmethod
    def _rot(i, j, k, A, B, C):
        """Rotaciona o ponto (i, j, k) pelos angulos A, B, C (mesma formula do
        IconCubePayload original do Win32-Payload-Engine)."""
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

    def _projetar(self, x, y, z, cx, cy, focal=400, dist=600):
        """Projeta um ponto 3D em 2D (perspectiva). Retorna (xp, yp, escala)."""
        z += dist
        if z <= 1:
            z = 1
        ooz = 1 / z
        xp = int(cx + focal * ooz * x)
        yp = int(cy - focal * ooz * y)
        escala = focal * ooz
        return xp, yp, escala

    # ------------------------------------------------------------------ #
    # Inicializacao das particulas de fogo.
    # ------------------------------------------------------------------ #
    def _iniciar(self, w, h):
        for _ in range(120):
            self.fire_particles.append(self._nova_particula(w, h, inicial=True))
        self._iniciado = True

    def _nova_particula(self, w, h, inicial=False):
        cx = w // 2
        return {
            "x": cx + random.randint(-int(w * 0.25), int(w * 0.25)),
            "y": random.randint(0, h) if inicial else h + random.randint(0, 40),
            "vy": random.uniform(2.5, 7.0),
            "tam": random.randint(2, 7),
            "quente": random.random() < 0.5,
        }

    # ------------------------------------------------------------------ #
    # Desenho de um pequeno olho (usado nos aneis).
    # ------------------------------------------------------------------ #
    def _desenhar_olho_pequeno(self, hdc, x, y, raio, cor_iris, aberto=True):
        if raio < 2:
            return
        # Esclera branca.
        esclera = win32gui.CreateSolidBrush(self.BRANCO)
        old = win32gui.SelectObject(hdc, esclera)
        win32gui.Ellipse(hdc, x - raio, y - int(raio * 0.7),
                         x + raio, y + int(raio * 0.7))
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(esclera)

        if not aberto:
            return

        # Iris.
        ir = int(raio * 0.7)
        iris = win32gui.CreateSolidBrush(cor_iris)
        old = win32gui.SelectObject(hdc, iris)
        win32gui.Ellipse(hdc, x - ir, y - ir, x + ir, y + ir)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(iris)

        # Pupila.
        pr = max(1, int(raio * 0.3))
        pupila = win32gui.CreateSolidBrush(self.PRETO)
        old = win32gui.SelectObject(hdc, pupila)
        win32gui.Ellipse(hdc, x - pr, y - pr, x + pr, y + pr)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(pupila)

    # ------------------------------------------------------------------ #
    # Desenho de um anel 3D coberto de olhos.
    # ------------------------------------------------------------------ #
    def _desenhar_anel(self, hdc, cx, cy, raio_base, angulo, tilt,
                       cor, n_olhos, cor_iris):
        """Desenha um anel (roda) em perspectiva 3D coberto de olhos.

        O anel e um circulo no plano XZ rotacionado por (tilt, angulo, 0).
        """
        pontos = []
        n = 48
        A = tilt          # inclinacao
        B = angulo        # rotacao principal (gira)
        C = tilt * 0.5
        for i in range(n + 1):
            t = 2 * math.pi * i / n
            # Circulo no plano XZ.
            ix = raio_base * math.cos(t)
            iy = 0
            iz = raio_base * math.sin(t)
            rx, ry, rz = self._rot(ix, iy, iz, A, B, C)
            xp, yp, _ = self._projetar(rx, ry, rz, cx, cy)
            pontos.append((xp, yp))

        # Desenha o aro do anel como linha espessa dourada.
        pen = win32gui.CreatePen(win32con.PS_SOLID, 6, cor)
        old = win32gui.SelectObject(hdc, pen)
        win32gui.MoveToEx(hdc, pontos[0][0], pontos[0][1])
        for (xp, yp) in pontos[1:]:
            win32gui.LineTo(hdc, xp, yp)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(pen)

        # Aro interno mais fino (brilho).
        pen2 = win32gui.CreatePen(win32con.PS_SOLID, 2, self.BRANCO)
        old = win32gui.SelectObject(hdc, pen2)
        win32gui.MoveToEx(hdc, pontos[0][0], pontos[0][1])
        for (xp, yp) in pontos[1:]:
            win32gui.LineTo(hdc, xp, yp)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(pen2)

        # Distribui olhos ao longo da circunferencia do anel.
        for e in range(n_olhos):
            t = 2 * math.pi * e / n_olhos
            ix = raio_base * math.cos(t)
            iy = 0
            iz = raio_base * math.sin(t)
            rx, ry, rz = self._rot(ix, iy, iz, A, B, C)
            xp, yp, escala = self._projetar(rx, ry, rz, cx, cy)
            raio_olho = max(2, int(10 * escala))
            # Olhos da frente (escala maior) piscam juntos ocasionalmente.
            aberto = not (int(self.frame / 25 + e) % 11 == 0)
            self._desenhar_olho_pequeno(hdc, xp, yp, raio_olho, cor_iris, aberto)

    # ------------------------------------------------------------------ #
    # Desenho do olho central gigante.
    # ------------------------------------------------------------------ #
    def _desenhar_olho_central(self, hdc, cx, cy, raio):
        # Abertura da palpebra (piscar dramatico).
        abertura = (math.sin(self.eye_blink) + 1) / 2
        abertura = 0.1 + abertura * 0.9
        ry = int(raio * abertura)

        preto = self.PRETO

        # Esclera amendoada via Polygon.
        pontos_cima, pontos_baixo = [], []
        n = 24
        for i in range(n + 1):
            t = -1 + 2 * i / n
            px = int(cx + t * raio)
            dy = int(ry * math.sqrt(max(0.0, 1 - t * t)))
            pontos_cima.append((px, cy - dy))
            pontos_baixo.append((px, cy + dy))
        contorno = pontos_cima + list(reversed(pontos_baixo))

        esclera = win32gui.CreateSolidBrush(self.rgb(250, 245, 235))
        pen = win32gui.CreatePen(win32con.PS_SOLID, 4, self.SANGUE)
        old_b = win32gui.SelectObject(hdc, esclera)
        old_p = win32gui.SelectObject(hdc, pen)
        win32gui.Polygon(hdc, contorno)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(esclera)

        if abertura > 0.2:
            # Veias vermelhas.
            veia = win32gui.CreatePen(win32con.PS_SOLID, 2, self.rgb(200, 40, 40))
            old_v = win32gui.SelectObject(hdc, veia)
            for _ in range(10):
                ang = random.uniform(0, 2 * math.pi)
                x1 = int(cx + raio * 0.8 * math.cos(ang))
                y1 = int(cy + ry * 0.8 * math.sin(ang))
                win32gui.MoveToEx(hdc, cx + random.randint(-10, 10), cy)
                win32gui.LineTo(hdc, x1, y1)
            win32gui.SelectObject(hdc, old_v)
            win32gui.DeleteObject(veia)

            # Iris dourada grande.
            ir = int(ry * 0.85)
            iris = win32gui.CreateSolidBrush(self.DOURADO)
            old_b = win32gui.SelectObject(hdc, iris)
            win32gui.Ellipse(hdc, cx - ir, cy - ir, cx + ir, cy + ir)
            win32gui.SelectObject(hdc, old_b)
            win32gui.DeleteObject(iris)

            # Anel escuro em volta da iris.
            aro = win32gui.CreatePen(win32con.PS_SOLID, 3, self.DOURADO_ESC)
            old_a = win32gui.SelectObject(hdc, aro)
            nb = win32gui.GetStockObject(win32con.NULL_BRUSH)
            old_nb = win32gui.SelectObject(hdc, nb)
            win32gui.Ellipse(hdc, cx - ir, cy - ir, cx + ir, cy + ir)
            win32gui.SelectObject(hdc, old_nb)
            win32gui.SelectObject(hdc, old_a)
            win32gui.DeleteObject(aro)

            # Pupila vermelho-sangue.
            pr = int(ir * 0.5)
            pupila = win32gui.CreateSolidBrush(self.VERMELHO)
            old_b = win32gui.SelectObject(hdc, pupila)
            win32gui.Ellipse(hdc, cx - pr, cy - pr, cx + pr, cy + pr)
            win32gui.SelectObject(hdc, old_b)
            win32gui.DeleteObject(pupila)

            # Nucleo preto da pupila.
            nr = int(pr * 0.5)
            nucleo = win32gui.CreateSolidBrush(preto)
            old_b = win32gui.SelectObject(hdc, nucleo)
            win32gui.Ellipse(hdc, cx - nr, cy - nr, cx + nr, cy + nr)
            win32gui.SelectObject(hdc, old_b)
            win32gui.DeleteObject(nucleo)

            # Brilho branco.
            brilho = win32gui.CreateSolidBrush(self.BRANCO)
            old_b = win32gui.SelectObject(hdc, brilho)
            bx, by = cx - pr // 2, cy - pr // 2
            win32gui.Ellipse(hdc, bx, by, bx + nr, by + nr)
            win32gui.SelectObject(hdc, old_b)
            win32gui.DeleteObject(brilho)

        win32gui.SelectObject(hdc, old_p)
        win32gui.DeleteObject(pen)

    # ------------------------------------------------------------------ #
    # Desenho das asas (Polygon com penas, batendo em onda).
    # ------------------------------------------------------------------ #
    def _desenhar_asa(self, hdc, cx, cy, escala, lado):
        """Desenha uma asa com varios segmentos de pena.

        :param lado: -1 para a asa esquerda, +1 para a direita.
        """
        n_penas = 6
        bat = math.sin(self.wing_phase)       # -1 .. 1 (batimento)
        penas = []
        for p in range(n_penas):
            frac = p / (n_penas - 1)
            # Angulo da pena: abre em leque; o batimento ergue/abaixa as penas.
            ang_base = math.radians(20 + frac * 90)
            ang = ang_base - bat * 0.4 * (1 + frac)
            comprimento = escala * (1.1 - frac * 0.45)

            base_x = cx + lado * escala * 0.15
            base_y = cy

            # Ponta da pena.
            px = base_x + lado * comprimento * math.cos(ang)
            py = base_y - comprimento * math.sin(ang) * 0.8 + frac * escala * 0.3

            # Largura da pena na base.
            larg = escala * 0.14
            perp = ang + math.pi / 2
            b1x = base_x + lado * larg * math.cos(perp)
            b1y = base_y - larg * math.sin(perp)
            b2x = base_x - lado * larg * math.cos(perp)
            b2y = base_y + larg * math.sin(perp)

            # Ponto de controle no meio (curva da pena).
            mx = (base_x + px) / 2 + lado * escala * 0.08
            my = (base_y + py) / 2

            pena = [
                (int(b1x), int(b1y)),
                (int(mx), int(my)),
                (int(px), int(py)),
                (int(b2x), int(b2y)),
            ]
            penas.append(pena)

        # Desenha as penas de tras para a frente (dourado -> branco nas pontas).
        for idx, pena in enumerate(penas):
            frac = idx / (n_penas - 1)
            r = int(255)
            g = int(215 - frac * 100)
            b = int(frac * 180)
            cor = self.rgb(r, g, b)
            brush = win32gui.CreateSolidBrush(cor)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 2, self.DOURADO_ESC)
            old_b = win32gui.SelectObject(hdc, brush)
            old_p = win32gui.SelectObject(hdc, pen)
            win32gui.Polygon(hdc, pena)
            win32gui.SelectObject(hdc, old_b)
            win32gui.SelectObject(hdc, old_p)
            win32gui.DeleteObject(brush)
            win32gui.DeleteObject(pen)

    # ------------------------------------------------------------------ #
    # Brilho / chama pulsante ao redor (elipses concentricas quentes).
    # ------------------------------------------------------------------ #
    def _desenhar_glow(self, hdc, cx, cy, raio_base):
        pulso = (math.sin(self.glow_pulse) + 1) / 2
        n = 8
        for i in range(n, 0, -1):
            frac = i / n
            r = int(raio_base * (1.0 + frac * 0.8) * (0.9 + pulso * 0.2))
            # Cores quentes do centro (dourado) para fora (vermelho-sangue).
            cr = int(255)
            cg = int(180 * (1 - frac))
            cb = int(0)
            cor = self.rgb(cr, cg, cb)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 3, cor)
            old = win32gui.SelectObject(hdc, pen)
            nb = win32gui.GetStockObject(win32con.NULL_BRUSH)
            old_b = win32gui.SelectObject(hdc, nb)
            win32gui.Ellipse(hdc, cx - r, cy - r, cx + r, cy + r)
            win32gui.SelectObject(hdc, old_b)
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(pen)

    # ------------------------------------------------------------------ #
    # Particulas de fogo subindo.
    # ------------------------------------------------------------------ #
    def _desenhar_fogo(self, hdc, w, h):
        for p in self.fire_particles:
            p["y"] -= p["vy"]
            p["x"] += random.randint(-1, 1)
            if p["y"] < -10:
                p.update(self._nova_particula(w, h))
            cor = self.FOGO if p["quente"] else self.rgb(255, 160, 0)
            brush = win32gui.CreateSolidBrush(cor)
            old = win32gui.SelectObject(hdc, brush)
            x, y, t = int(p["x"]), int(p["y"]), p["tam"]
            win32gui.Ellipse(hdc, x, y, x + t, y + t)
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(brush)

    # ------------------------------------------------------------------ #
    # Texto sagrado flutuante.
    # ------------------------------------------------------------------ #
    def _desenhar_texto(self, hdc, cx, cy, raio):
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        pulso = (math.sin(self.glow_pulse) + 1) / 2
        brilho = int(150 + pulso * 105)
        win32gui.SetTextColor(hdc, self.rgb(brilho, brilho // 2, 0))

        fonte = criar_fonte(-int(raio * 0.18), peso=win32con.FW_BOLD,
                            face="Georgia")
        if fonte is not None:
            old = win32gui.SelectObject(hdc, fonte)
        texto = "KADOSH  KADOSH  KADOSH"
        # Centraliza aproximadamente o texto acima do anjo.
        tx = cx - int(len(texto) * raio * 0.045)
        win32gui.TextOut(hdc, tx, cy - int(raio * 2.1), texto)
        win32gui.TextOut(hdc, tx + 20, cy + int(raio * 1.9), "SANTO SANTO SANTO")
        if fonte is not None:
            win32gui.SelectObject(hdc, old)

    # ------------------------------------------------------------------ #
    # Quadro principal.
    # ------------------------------------------------------------------ #
    def draw(self, hdc, w, h):
        if not self._iniciado:
            self._iniciar(w, h)

        cx, cy = w // 2, h // 2
        raio_base = int(min(w, h) * 0.18)

        # Fundo preto.
        win32gui.PatBlt(hdc, 0, 0, w, h, win32con.BLACKNESS)

        # 1) Particulas de fogo ao fundo.
        self._desenhar_fogo(hdc, w, h)

        # 2) Brilho/chama pulsante.
        self._desenhar_glow(hdc, cx, cy, raio_base)

        # 3) Asas batendo (desenhadas atras dos aneis).
        self._desenhar_asa(hdc, cx, cy, raio_base * 1.6, lado=-1)
        self._desenhar_asa(hdc, cx, cy, raio_base * 1.6, lado=+1)

        # 4) Tres aneis concentricos girando em perspectiva 3D.
        #    Cada anel com raio, velocidade, inclinacao e cor proprios.
        self._desenhar_anel(hdc, cx, cy, int(raio_base * 1.9),
                            self.ring_angles[0], self.ring_tilts[0],
                            self.DOURADO, 22, self.VERMELHO)
        self._desenhar_anel(hdc, cx, cy, int(raio_base * 1.45),
                            self.ring_angles[1], self.ring_tilts[1],
                            self.DOURADO_ESC, 18, self.DOURADO)
        self._desenhar_anel(hdc, cx, cy, int(raio_base * 1.0),
                            self.ring_angles[2], self.ring_tilts[2],
                            self.SANGUE, 14, self.VERMELHO)

        # 5) Olho central gigante.
        self._desenhar_olho_central(hdc, cx, cy, int(raio_base * 0.55))

        # 6) Texto sagrado flutuante.
        self._desenhar_texto(hdc, cx, cy, raio_base)

        # --- Atualiza estados de animacao ---
        for i in range(3):
            self.ring_angles[i] += self.ring_speeds[i]
            self.ring_tilts[i] = math.sin(self.frame * 0.01 + i) * 0.6
        self.eye_blink += 0.08
        self.wing_phase += 0.12
        self.glow_pulse += 0.06
        self.frame += 1
