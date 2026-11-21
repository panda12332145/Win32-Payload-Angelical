# -*- coding: utf-8 -*-
"""ANJO TRONO (OPHANIM) — engine OpenGL (3D).

Recriação do anjo biblico (Ezequiel 1 e 10) em perspectiva 3D real, desenhada
com o Renderer OpenGL:
  * 3 anéis concêntricos girando em velocidades/direções diferentes,
    cobertos de olhos (rotação 3D + projeção em perspectiva);
  * olho central gigante com piscar dramático, iris dourada, pupila
    vermelho-sangue e brilho branco;
  * 2 asas simétricas com 6 penas cada, batendo em onda senoidal;
  * partículas de fogo e poeira dourada subindo ao fundo;
  * brilho quente pulsante (mistura aditiva);
  * texto sagrado na fonte bitmap (KADOSH / SANTO).

Todos os estados de animação são dt-based (tempo real), não frame-based.
"""

import math
import random

from .base import GlEffect
from .math_3d import rot, project

_GOLD = (1.0, 0.84, 0.0)
_GOLD_DARK = (0.7, 0.55, 0.0)
_CRIMSON = (0.86, 0.08, 0.24)
_SANGUE = (0.55, 0.0, 0.0)
_FIRE = (1.0, 0.27, 0.0)
_ORANGE = (1.0, 0.63, 0.0)


class OphanimAngelGl(GlEffect):
    name = "Anjo Trono (Ophanim)"
    description = "Anjo biblico 3D: anéis girando com olhos, olho central, asas batendo, fogo e brilho."

    def __init__(self):
        super().__init__()
        self.ring_angles = [0.0, 0.0, 0.0]
        self.ring_speeds = [2.4, -1.8, 1.2]   # rad/s
        self.eye_blink = 0.0
        self.wing_phase = 0.0
        self.glow_pulse = 0.0
        self.fire = []
        self.dust = []
        self.veins = []
        self._iniciado = False

    # ------------------------------------------------------------------ #
    def _iniciar(self, w, h):
        cx = w // 2
        for _ in range(90):
            self.fire.append({
                "x": cx + random.uniform(-w * 0.30, w * 0.30),
                "y": random.uniform(0, h),
                "vy": random.uniform(150, 420),
                "tam": random.uniform(2, 7),
                "quente": random.random() < 0.5,
                "alpha": random.uniform(0.5, 0.95),
            })
        for _ in range(46):
            self.dust.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "vy": random.uniform(6, 26),
                "dx": random.uniform(-6, 6),
                "tam": random.uniform(1.5, 3.5),
                "fase": random.uniform(0, 2 * math.pi),
            })
        # Veias do olho central (ângulos fixos para nao piscarem).
        self.veins = [random.uniform(0, 2 * math.pi) for _ in range(12)]
        self._iniciado = True

    # ------------------------------------------------------------------ #
    def update(self, dt, w, h, t):
        if not self._iniciado:
            self._iniciar(w, h)
        for i in range(3):
            self.ring_angles[i] += self.ring_speeds[i] * dt
        self.eye_blink += dt * 4.8
        self.wing_phase += dt * 7.2
        self.glow_pulse += dt * 3.6

        for p in self.fire:
            p["y"] -= p["vy"] * dt
            p["x"] += random.uniform(-30, 30) * dt
            if p["y"] < -20:
                p["x"] = w // 2 + random.uniform(-w * 0.30, w * 0.30)
                p["y"] = h + random.uniform(0, 60)
                p["vy"] = random.uniform(150, 420)
                p["tam"] = random.uniform(2, 7)
                p["quente"] = random.random() < 0.5
                p["alpha"] = random.uniform(0.5, 0.95)

        for p in self.dust:
            p["y"] -= p["vy"] * dt
            p["x"] += p["dx"] * dt
            if p["y"] < -10:
                p["y"] = h + 10
                p["x"] = random.uniform(0, w)

    # ------------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------------ #
    def draw(self, r, w, h, t):
        cx = w * 0.5 + math.sin(t * 0.23) * 6.0
        cy = h * 0.5 + math.cos(t * 0.19) * 5.0
        raio_base = min(w, h) * 0.18
        focal = min(w, h) * 0.9
        dist = focal * 1.6

        # --- Fundo: preto com leve vinheta avermelhada ---
        r.clear(0.015, 0.008, 0.02, 1.0)
        r.use_additive()
        brilho_fondo = math.sin(self.glow_pulse) * 0.5 + 0.5
        for i in range(10, 0, -1):
            frac = i / 10.0
            rr = raio_base * (2.6 + frac * 3.4) * (0.92 + brilho_fondo * 0.16)
            rg = 0.30 * (1 - frac) + 0.05
            r.ellipse(cx, cy, rr, rr * 0.82,
                      0.35, rg * 0.10, 0.02, 0.05 + 0.05 * (1 - frac))
        r.flush()

        # --- Partículas de fogo (profundidade: atras) ---
        for p in self.fire:
            col = _FIRE if p["quente"] else _ORANGE
            r.use_additive()
            r.ellipse(p["x"], p["y"], p["tam"], p["tam"] * 1.25,
                      col[0], col[1], col[2], p["alpha"] * 0.9, seg=8)
        r.flush()

        # --- Brilho quente pulsante (anéis concêntricos, aditivo) ---
        pulse = (math.sin(self.glow_pulse) + 1.0) / 2.0
        r.use_additive()
        n_glow = 9
        for i in range(n_glow, 0, -1):
            frac = i / n_glow
            rr = raio_base * (1.15 + frac * 1.05) * (0.90 + pulse * 0.18)
            cg = 0.72 * (1 - frac) + 0.06
            r.ring_ellipse(cx, cy, rr, rr * 0.86, rr * 0.72, rr * 0.72 * 0.86,
                           1.0, cg, 0.02, 0.05 + 0.09 * (1 - frac), seg=48)
        r.flush()

        # --- Asas ---
        self._draw_asa(r, cx, cy, raio_base * 1.62, -1)
        self._draw_asa(r, cx, cy, raio_base * 1.62, +1)

        # --- Três anéis 3D cobertos de olhos ---
        aneis = (
            # (escala do raio, velocidade, tilt-fase, olhos, iris_kind, cor)
            (1.92, 0, 24, "vermelho", _GOLD, 0.0),
            (1.45, 1, 19, "dourado", _GOLD_DARK, 1.1),
            (1.02, 2, 15, "vermelho", _SANGUE, 2.2),
        )
        for i, (esc, ridx, n_olhos, iris_kind, aro_cor, tilt_fase) in enumerate(aneis):
            tilt = math.sin(t * 0.6 + tilt_fase) * 0.58
            rot_a = self.ring_angles[ridx]
            cor_iris = _CRIMSON if iris_kind == "vermelho" else _GOLD
            self._draw_anel(r, cx, cy, raio_base * esc,
                            rot_a, tilt, aro_cor, n_olhos, cor_iris,
                            focal, dist, t)

        # --- Olho central ---
        self._draw_olho_central(r, cx, cy, raio_base * 0.55, t)

        # --- Poeira dourada ---
        r.use_additive()
        for p in self.dust:
            alpha = 0.16 + 0.14 * math.sin(t * 1.7 + p["fase"])
            r.point(p["x"], p["y"], p["tam"], 1.0, 0.8, 0.25, max(0.0, alpha))
        r.flush()

        # --- Texto sagrado ---
        alfa = 0.45 + 0.4 * pulse
        r.text("KADOSH  KADOSH  KADOSH", cx, cy - raio_base * 2.15,
               3, 1.0, 0.80, 0.10, alfa, align='center')
        r.text("SANTO  SANTO  SANTO", cx, cy + raio_base * 1.95,
               3, 1.0, 0.72, 0.10, alfa * 0.9, align='center')

    # ------------------------------------------------------------------ #
    # Anel 3D
    # ------------------------------------------------------------------ #
    def _draw_anel(self, r, cx, cy, raio, angulo, tilt, cor, n_olhos,
                   cor_iris, focal, dist, t):
        A = tilt
        B = angulo
        C = tilt * 0.5
        n = 56
        pontos_p = []
        for i in range(n + 1):
            t0 = 2 * math.pi * i / n
            ix = raio * math.cos(t0)
            iz = raio * math.sin(t0)
            rx, ry, rz = rot(ix, 0, iz, A, B, C)
            xp, yp, escala = project(rx, ry, rz, cx, cy, focal, dist)
            pontos_p.append((xp, yp, escala))

        # Aro externo espesso (dourado)
        self._thick_ring(r, pontos_p, 7.0, cor, 0.95, focal, dist)
        # Aro interno fino (brilho branco)
        self._thick_ring(r, pontos_p, 2.2, (1.0, 1.0, 1.0), 0.60, focal, dist)

        # Olhos distribuídos pela circunferencia
        for e in range(n_olhos):
            t0 = 2 * math.pi * e / n_olhos
            ix = raio * math.cos(t0)
            iz = raio * math.sin(t0)
            rx, ry, rz = rot(ix, 0, iz, A, B, C)
            xp, yp, escala = project(rx, ry, rz, cx, cy, focal, dist)
            raio_olho = max(2.5, 10.0 * escala * 1.9)
            if raio_olho < 2.0:
                continue
            aberto = not (int(t * 2.5 + e) % 11 == 0)
            self._draw_olho_pequeno(r, xp, yp, raio_olho, cor_iris, aberto)

    def _thick_ring(self, r, pontos_p, largura, cor, alpha, focal, dist):
        for i in range(len(pontos_p) - 1):
            x1, y1, s1 = pontos_p[i]
            x2, y2, s2 = pontos_p[i + 1]
            lw = max(1.2, largura * (s1 + s2) * 0.5 * 2.2)
            r.thick_line(x1, y1, x2, y2, lw, cor[0], cor[1], cor[2], alpha)

    def _draw_olho_pequeno(self, r, x, y, raio, cor_iris, aberto):
        # Esclera (branco)
        r.ellipse(x, y, raio * 1.05, raio * 0.68, 0.96, 0.93, 0.88, 0.98, seg=14)
        if not aberto:
            r.thick_line(x - raio * 0.8, y, x + raio * 0.8, y, 1.4, 0.10, 0.06, 0.06, 1.0)
            return
        # Iris
        ir = raio * 0.62
        r.ellipse(x, y, ir, ir * 0.95, cor_iris[0], cor_iris[1], cor_iris[2], 0.98, seg=12)
        # Pupila
        pr = raio * 0.28
        r.ellipse(x, y, pr, pr, 0.02, 0.02, 0.02, 1.0, seg=8)

    # ------------------------------------------------------------------ #
    # Olho central
    # ------------------------------------------------------------------ #
    def _draw_olho_central(self, r, cx, cy, raio, t):
        abertura = (math.sin(self.eye_blink) + 1) / 2.0
        abertura = 0.12 + abertura * 0.88
        ry = max(2.0, raio * abertura)

        # Esclera (contorno amendoado)
        n = 28
        cima, baixo = [], []
        for i in range(n + 1):
            tt = -1 + 2 * i / n
            px = cx + tt * raio
            dy = ry * math.sqrt(max(0.0, 1 - tt * tt))
            cima.append((px, cy - dy))
            baixo.append((px, cy + dy))
        contorno = cima + list(reversed(baixo))
        r.poly(contorno, 0.97, 0.94, 0.90, 0.98)

        if abertura > 0.25:
            # Veias (ângulos fixos, leve pulsação de alpha)
            alfa_veia = 0.28 + 0.18 * math.sin(t * 2.1)
            for veia_ang in self.veins:
                vx = cx + math.cos(veia_ang) * raio * 0.82
                vy = cy + math.sin(veia_ang) * ry * 0.82
                r.thick_line(cx, cy, vx, vy, 1.5, 0.78, 0.10, 0.10, alfa_veia)
            # Iris dourada
            ir = ry * 0.88
            cor_iris = _GOLD
            r.ellipse(cx, cy, ir, ir * 0.92, cor_iris[0], cor_iris[1], cor_iris[2], 0.98, seg=28)
            # Anel externo da iris (ouro escuro)
            r.ring_ellipse(cx, cy, ir, ir * 0.92, ir * 0.90, ir * 0.84,
                           _GOLD_DARK[0], _GOLD_DARK[1], _GOLD_DARK[2], 0.95, seg=28)
            # Pupila vermelha-escura
            pr = ir * 0.50
            r.ellipse(cx, cy, pr, pr * 0.96, 0.55, 0.02, 0.04, 1.0, seg=20)
            # Nucleo preto
            nr = pr * 0.48
            r.ellipse(cx, cy, nr, nr, 0.01, 0.01, 0.01, 1.0, seg=14)
            # Brilho
            bx = cx - pr * 0.45
            by = cy - pr * 0.45
            r.ellipse(bx, by, nr * 0.52, nr * 0.52, 1.0, 1.0, 1.0, 0.98, seg=10)
        else:
            # Palpebra fechada: linha fina
            r.thick_line(cx - raio * 0.85, cy, cx + raio * 0.85, cy, 3.0,
                         0.45, 0.18, 0.12, 0.95)

    # ------------------------------------------------------------------ #
    # Asas
    # ------------------------------------------------------------------ #
    def _draw_asa(self, r, cx, cy, escala, lado):
        bat = math.sin(self.wing_phase)
        n_penas = 6
        penas = []
        for p in range(n_penas):
            frac = p / (n_penas - 1)
            ang_base = math.radians(16 + frac * 96)
            ang = ang_base - bat * 0.42 * (1 + frac)
            comprimento = escala * (1.12 - frac * 0.45)
            base_x = cx + lado * escala * 0.14
            base_y = cy
            px = base_x + lado * comprimento * math.cos(ang)
            py = base_y - comprimento * math.sin(ang) * 0.78 + frac * escala * 0.30
            larg = escala * 0.135
            perp = ang + math.pi / 2
            b1x = base_x + lado * larg * math.cos(perp)
            b1y = base_y - larg * math.sin(perp)
            b2x = base_x - lado * larg * math.cos(perp)
            b2y = base_y + larg * math.sin(perp)
            mx = (base_x + px) / 2 + lado * escala * 0.085
            my = (base_y + py) / 2
            penas.append([(b1x, b1y), (mx, my), (px, py), (b2x, b2y)])

        for idx, pena in enumerate(penas):
            frac = idx / (n_penas - 1)
            g = 0.84 - frac * 0.45
            b = frac * 0.85
            r.poly(pena, 1.0, g, b, 0.96)
            r.thick_line(pena[0][0], pena[0][1], pena[2][0], pena[2][1],
                         1.6, 0.72, 0.56, 0.10, 0.85)
