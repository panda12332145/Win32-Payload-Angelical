# -*- coding: utf-8 -*-
"""Payloads de TERROR (tema: horror visual).

Contem:
  * BloodDropPayload    -> gotas de sangue escorrendo e acumulando (stateful).
  * CracksPayload       -> rachaduras se espalhando pela tela (stateful).
  * ShadowFigurePayload -> silhueta sombria que aparece/some em fade (stateful).
  * SkullPayload        -> cranios desenhados em GDI.
  * DarknessPayload     -> vinheta de escuridao pulsante com estrelas (stateful).
"""

import math
import random

import win32con
import win32gui

from .base import Payload


class BloodDropPayload(Payload):
    """Gotas de sangue caindo pela tela com aceleracao e acumulo no fundo.

    Payload com estado: cada gota mantem posicao e velocidade; ao atingir o
    fundo (ou uma poca ja acumulada) ela contribui para uma "poca" crescente.
    """

    name = "Sangue Escorrendo"
    description = "Gotas de sangue caem, aceleram e se acumulam no fundo."
    stateful = True

    def __init__(self):
        self.gotas = []          # cada gota: dict(x, y, vy, comprimento, largura)
        self.poca = {}           # coluna x -> altura acumulada no fundo
        self._iniciado = False

    def _iniciar(self, w, h):
        self.largura_tela = w
        self.altura_tela = h
        for _ in range(60):
            self.gotas.append(self._nova_gota(w, h, topo=True))
        self._iniciado = True

    def _nova_gota(self, w, h, topo=False):
        return {
            "x": random.randint(0, w),
            "y": random.randint(-h, 0) if topo else random.randint(-200, -10),
            "vy": random.uniform(2, 6),
            "comprimento": random.randint(20, 90),
            "largura": random.randint(2, 6),
        }

    def draw(self, hdc, w, h):
        if not self._iniciado:
            self._iniciar(w, h)

        # Desenha a poca acumulada no fundo.
        for col_x, altura in self.poca.items():
            if altura <= 0:
                continue
            brush = win32gui.CreateSolidBrush(self.rgb(100, 0, 0))
            win32gui.FillRect(hdc, (col_x, h - int(altura), col_x + 8, h), brush)
            win32gui.DeleteObject(brush)

        # Atualiza e desenha cada gota.
        for gota in self.gotas:
            gota["vy"] += 0.25           # gravidade (aceleracao)
            gota["y"] += gota["vy"]

            x = int(gota["x"])
            y = int(gota["y"])
            comp = gota["comprimento"]
            larg = gota["largura"]

            # Corpo da gota (retangulo vermelho escuro) + cabeca arredondada.
            brush = win32gui.CreateSolidBrush(self.rgb(139, 0, 0))
            win32gui.FillRect(hdc, (x, y, x + larg, y + comp), brush)
            win32gui.DeleteObject(brush)

            cabeca = win32gui.CreateSolidBrush(self.rgb(180, 10, 10))
            old = win32gui.SelectObject(hdc, cabeca)
            win32gui.Ellipse(hdc, x - 2, y + comp - 4, x + larg + 2, y + comp + 6)
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(cabeca)

            # Quando chega ao fundo, acumula na poca e renasce no topo.
            col = (x // 8) * 8
            altura_poca = self.poca.get(col, 0)
            if y + comp >= h - altura_poca:
                self.poca[col] = min(altura_poca + comp * 0.15, h * 0.4)
                gota.update(self._nova_gota(w, h))


class CracksPayload(Payload):
    """Rachaduras que se espalham recursivamente a partir de pontos da tela.

    Payload com estado: as rachaduras crescem um pouco a cada quadro.
    """

    name = "Rachaduras"
    description = "Rachaduras negras se espalhando pela tela."
    stateful = True

    def __init__(self):
        self.pontas = []     # pontas ativas: dict(x, y, ang, vida)
        self.segmentos = []  # segmentos ja desenhados: (x1, y1, x2, y2)
        self._iniciado = False

    def _iniciar(self, w, h):
        for _ in range(4):
            self.pontas.append({
                "x": random.randint(int(w * 0.2), int(w * 0.8)),
                "y": random.randint(int(h * 0.2), int(h * 0.8)),
                "ang": random.uniform(0, 2 * math.pi),
                "vida": random.randint(40, 90),
            })
        self._iniciado = True

    def draw(self, hdc, w, h):
        if not self._iniciado:
            self._iniciar(w, h)

        # Faz as pontas ativas avancarem, criando novos segmentos.
        novas = []
        for ponta in self.pontas:
            if ponta["vida"] <= 0:
                continue
            passo = random.randint(8, 22)
            ponta["ang"] += random.uniform(-0.4, 0.4)
            nx = ponta["x"] + passo * math.cos(ponta["ang"])
            ny = ponta["y"] + passo * math.sin(ponta["ang"])
            self.segmentos.append((int(ponta["x"]), int(ponta["y"]),
                                   int(nx), int(ny)))
            ponta["x"], ponta["y"] = nx, ny
            ponta["vida"] -= 1

            # Chance de bifurcar criando uma nova ponta.
            if random.random() < 0.08 and len(self.pontas) + len(novas) < 40:
                novas.append({
                    "x": nx, "y": ny,
                    "ang": ponta["ang"] + random.uniform(-1.2, 1.2),
                    "vida": ponta["vida"] // 2,
                })
            if 0 <= nx <= w and 0 <= ny <= h:
                novas.append(ponta)
        self.pontas = novas

        # Reinicia quando todas as rachaduras terminam.
        if not self.pontas:
            self.segmentos = []
            self._iniciar(w, h)

        # Desenha todos os segmentos: borda branca grossa + linha preta fina.
        pen_borda = win32gui.CreatePen(win32con.PS_SOLID, 3, self.rgb(220, 220, 220))
        old = win32gui.SelectObject(hdc, pen_borda)
        for (x1, y1, x2, y2) in self.segmentos:
            win32gui.MoveToEx(hdc, x1, y1)
            win32gui.LineTo(hdc, x2, y2)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(pen_borda)

        pen_nucleo = win32gui.CreatePen(win32con.PS_SOLID, 1, self.rgb(0, 0, 0))
        old = win32gui.SelectObject(hdc, pen_nucleo)
        for (x1, y1, x2, y2) in self.segmentos:
            win32gui.MoveToEx(hdc, x1, y1)
            win32gui.LineTo(hdc, x2, y2)
        win32gui.SelectObject(hdc, old)
        win32gui.DeleteObject(pen_nucleo)


class ShadowFigurePayload(Payload):
    """Silhueta humanoide sombria que aparece e desaparece em fade.

    Payload com estado: controla a fase do fade e a posicao horizontal.
    """

    name = "Figura Sombria"
    description = "Uma silhueta humanoide surge lentamente das trevas."
    stateful = True

    def __init__(self):
        self.fase = 0.0          # avanca continuamente (seno controla opacidade)
        self.base_x = None

    def draw(self, hdc, w, h):
        if self.base_x is None:
            self.base_x = w // 2

        self.fase += 0.04
        # Intensidade entre 0 e 1 (pulso suave de aparecer/sumir).
        intensidade = (math.sin(self.fase) + 1) / 2

        # Reposiciona a figura quando praticamente invisivel.
        if intensidade < 0.03:
            self.base_x = random.randint(int(w * 0.2), int(w * 0.8))

        # Cor do preto ao cinza simulando a "densidade" da sombra.
        tom = int(10 + intensidade * 35)
        cor = self.rgb(tom, tom, tom)
        brush = win32gui.CreateSolidBrush(cor)
        pen = win32gui.CreatePen(win32con.PS_SOLID, 1, cor)
        old_b = win32gui.SelectObject(hdc, brush)
        old_p = win32gui.SelectObject(hdc, pen)

        cx = self.base_x
        topo = int(h * 0.25)
        escala = h * 0.5

        # Cabeca (elipse).
        cabeca_r = int(escala * 0.09)
        win32gui.Ellipse(hdc, cx - cabeca_r, topo,
                         cx + cabeca_r, topo + 2 * cabeca_r)

        # Tronco (poligono trapezoidal de ombros a quadril).
        ombro_y = topo + 2 * cabeca_r
        quadril_y = int(topo + escala * 0.8)
        tronco = [
            (cx - int(escala * 0.14), ombro_y),
            (cx + int(escala * 0.14), ombro_y),
            (cx + int(escala * 0.10), quadril_y),
            (cx - int(escala * 0.10), quadril_y),
        ]
        win32gui.Polygon(hdc, tronco)

        # Bracos (linhas grossas descendo pelos lados).
        braco_pen = win32gui.CreatePen(win32con.PS_SOLID,
                                       max(2, int(escala * 0.04)), cor)
        old_bp = win32gui.SelectObject(hdc, braco_pen)
        win32gui.MoveToEx(hdc, cx - int(escala * 0.13), ombro_y + 6)
        win32gui.LineTo(hdc, cx - int(escala * 0.20), quadril_y)
        win32gui.MoveToEx(hdc, cx + int(escala * 0.13), ombro_y + 6)
        win32gui.LineTo(hdc, cx + int(escala * 0.20), quadril_y)
        win32gui.SelectObject(hdc, old_bp)
        win32gui.DeleteObject(braco_pen)

        # Olhos vermelhos brilhando quando a figura esta mais visivel.
        if intensidade > 0.5:
            olho = win32gui.CreateSolidBrush(self.rgb(int(200 * intensidade), 0, 0))
            old_o = win32gui.SelectObject(hdc, olho)
            oy = topo + cabeca_r - 2
            win32gui.Ellipse(hdc, cx - cabeca_r + 4, oy, cx - 2, oy + 5)
            win32gui.Ellipse(hdc, cx + 2, oy, cx + cabeca_r - 4, oy + 5)
            win32gui.SelectObject(hdc, old_o)
            win32gui.DeleteObject(olho)

        win32gui.SelectObject(hdc, old_b)
        win32gui.SelectObject(hdc, old_p)
        win32gui.DeleteObject(brush)
        win32gui.DeleteObject(pen)


class SkullPayload(Payload):
    """Cranios desenhados com primitivas GDI espalhados pela tela."""

    name = "Cranios"
    description = "Cranios fantasmagoricos desenhados em GDI."
    stateful = False

    def _desenhar_cranio(self, hdc, cx, cy, tam):
        """Desenha um unico cranio centrado em (cx, cy) com largura ~ tam."""
        branco = self.rgb(230, 230, 220)
        preto = self.rgb(0, 0, 0)

        # Cranio (oval superior).
        brush = win32gui.CreateSolidBrush(branco)
        pen = win32gui.CreatePen(win32con.PS_SOLID, 1, preto)
        old_b = win32gui.SelectObject(hdc, brush)
        old_p = win32gui.SelectObject(hdc, pen)
        win32gui.Ellipse(hdc, cx - tam // 2, cy - tam // 2,
                         cx + tam // 2, cy + int(tam * 0.3))

        # Mandibula (retangulo arredondado abaixo do cranio).
        win32gui.RoundRect(hdc, cx - tam // 4, cy + int(tam * 0.15),
                           cx + tam // 4, cy + int(tam * 0.55),
                           tam // 6, tam // 6)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(brush)

        # Orbitas oculares (duas elipses pretas).
        orbita = win32gui.CreateSolidBrush(preto)
        old_b = win32gui.SelectObject(hdc, orbita)
        olho_w = tam // 5
        olho_h = int(tam * 0.22)
        oy = cy - tam // 8
        win32gui.Ellipse(hdc, cx - tam // 4 - 2, oy,
                         cx - tam // 4 + olho_w, oy + olho_h)
        win32gui.Ellipse(hdc, cx + tam // 4 - olho_w, oy,
                         cx + tam // 4 + 2, oy + olho_h)

        # Nariz (triangulo preto).
        nariz = [
            (cx, cy + int(tam * 0.02)),
            (cx - tam // 12, cy + int(tam * 0.15)),
            (cx + tam // 12, cy + int(tam * 0.15)),
        ]
        win32gui.Polygon(hdc, nariz)
        win32gui.SelectObject(hdc, old_b)
        win32gui.DeleteObject(orbita)

        # Dentes (pequenos retangulos brancos sobre a mandibula).
        dente_pen = win32gui.CreatePen(win32con.PS_SOLID, 1, preto)
        old_dp = win32gui.SelectObject(hdc, dente_pen)
        nb = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        old_nb = win32gui.SelectObject(hdc, nb)
        dente_y = cy + int(tam * 0.18)
        dente_w = tam // 10
        for i in range(4):
            dx = cx - tam // 5 + i * dente_w
            win32gui.Rectangle(hdc, dx, dente_y, dx + dente_w - 2,
                               dente_y + int(tam * 0.12))
        win32gui.SelectObject(hdc, old_nb)
        win32gui.SelectObject(hdc, old_dp)
        win32gui.DeleteObject(dente_pen)

        win32gui.SelectObject(hdc, old_p)
        win32gui.DeleteObject(pen)

    def draw(self, hdc, w, h):
        # Fundo preto para dar o clima.
        win32gui.PatBlt(hdc, 0, 0, w, h, win32con.BLACKNESS)
        for _ in range(8):
            tam = random.randint(80, 220)
            cx = random.randint(tam, max(w - tam, tam + 1))
            cy = random.randint(tam, max(h - tam, tam + 1))
            self._desenhar_cranio(hdc, cx, cy, tam)


class DarknessPayload(Payload):
    """Vinheta de escuridao pulsante com estrelas distantes.

    Payload com estado: o raio da area clara pulsa suavemente.
    """

    name = "Escuridao"
    description = "Trevas pulsantes consumindo a tela, com estrelas distantes."
    stateful = True

    def __init__(self):
        self.fase = 0.0
        self.estrelas = []
        self._iniciado = False

    def _iniciar(self, w, h):
        for _ in range(120):
            self.estrelas.append((random.randint(0, w), random.randint(0, h),
                                  random.randint(1, 3)))
        self._iniciado = True

    def draw(self, hdc, w, h):
        if not self._iniciado:
            self._iniciar(w, h)

        self.fase += 0.05
        pulso = (math.sin(self.fase) + 1) / 2   # 0..1

        # Aneis concentricos escurecendo das bordas para o centro.
        cx, cy = w // 2, h // 2
        max_r = int(math.hypot(w, h) / 2)
        # Raio da area ainda visivel (pulsa).
        raio_claro = int(max_r * (0.25 + pulso * 0.25))

        n_aneis = 40
        for i in range(n_aneis, 0, -1):
            r = int(max_r * i / n_aneis)
            if r < raio_claro:
                break
            # Mais escuro quanto mais longe do centro.
            escuridao = int(255 * (1 - i / n_aneis))
            tom = max(0, 30 - escuridao)
            pen = win32gui.CreatePen(win32con.PS_SOLID, max_r // n_aneis + 2,
                                     self.rgb(tom, 0, 0))
            old = win32gui.SelectObject(hdc, pen)
            nb = win32gui.GetStockObject(win32con.NULL_BRUSH)
            old_b = win32gui.SelectObject(hdc, nb)
            win32gui.Ellipse(hdc, cx - r, cy - r, cx + r, cy + r)
            win32gui.SelectObject(hdc, old_b)
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(pen)

        # Estrelas distantes (pontos brancos tremeluzentes).
        for (sx, sy, sr) in self.estrelas:
            if random.random() < 0.7:
                brilho = random.randint(120, 255)
                brush = win32gui.CreateSolidBrush(self.rgb(brilho, brilho, brilho))
                old = win32gui.SelectObject(hdc, brush)
                win32gui.Ellipse(hdc, sx, sy, sx + sr, sy + sr)
                win32gui.SelectObject(hdc, old)
                win32gui.DeleteObject(brush)
