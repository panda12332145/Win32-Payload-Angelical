# -*- coding: utf-8 -*-
"""Renderer OpenGL dos efeitos 3D / poligonos / texto.

Desenha a partir de listas de triangulos com cor RGBA por vertice, usando
blending com alpha e MSAA (anti-aliasing) — coisa que GDI nao consegue fazer.

Cada frame:
  1. o efeito constroi geometria via ``rect``/``ellipse``/``poly``/``thick_line``/``text``
     (os verts sao armazenados em ``self.tris`` na coordenada de tela);
  2. ``flush()`` converte para NDC, sobe para a GPU e desenha em uma
     unica chamada a ``glDrawArrays``.
"""

import math
import struct

from .font import FONT_5x7

_VERT = """#version 330 core
layout(location = 0) in vec2 iPos;
layout(location = 1) in vec4 iColor;
out vec4 vColor;
void main() {
    vColor = iColor;
    gl_Position = vec4(iPos, 0.0, 1.0);
}"""

_FRAG = """#version 330 core
in vec4 vColor;
out vec4 frag;
void main() {
    frag = vColor;
}"""


def _shader(gl, src, tipo):
    shader = gl.glCreateShader(tipo)
    gl.glShaderSource(shader, src)
    gl.glCompileShader(shader)
    res = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    ok = res[0] if isinstance(res, (tuple, list)) else res
    if not ok:
        log = gl.glGetShaderInfoLog(shader)
        if isinstance(log, bytes):
            log = log.decode('utf-8', 'replace')
        gl.glDeleteShader(shader)
        raise RuntimeError('Erro ao compilar shader:\n' + str(log))
    return shader


def _link(gl, vert, frag):
    prog = gl.glCreateProgram()
    gl.glAttachShader(prog, vert)
    gl.glAttachShader(prog, frag)
    gl.glLinkProgram(prog)
    res = gl.glGetProgramiv(prog, gl.GL_LINK_STATUS)
    ok = res[0] if isinstance(res, (tuple, list)) else res
    if not ok:
        log = gl.glGetProgramInfoLog(prog)
        if isinstance(log, bytes):
            log = log.decode('utf-8', 'replace')
        gl.glDeleteProgram(prog)
        raise RuntimeError('Erro ao linkar shader:\n' + str(log))
    return prog


class Renderer(object):
    """Rastreador de geometria + desenho em uma unica chamada por frame."""

    def __init__(self, gl, w, h):
        self.gl = gl
        self.w = float(w)
        self.h = float(h)
        self.tris = []
        self._additive = False
        self._build()

    def use_additive(self, on=True):
        """Muda o modo de mistura para aditivo (glow). Reset a cada flush."""
        self._additive = bool(on)

    # ------------------------------------------------------------------ #
    # Setup interna
    # ------------------------------------------------------------------ #
    def _build(self):
        gl = self.gl
        vert = _shader(gl, _VERT, gl.GL_VERTEX_SHADER)
        frag = _shader(gl, _FRAG, gl.GL_FRAGMENT_SHADER)
        self.prog = _link(gl, vert, frag)
        gl.glDeleteShader(vert)
        gl.glDeleteShader(frag)

        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 24, b'\x00')
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 4, gl.GL_FLOAT, False, 24, b'\x08')
        gl.glBindVertexArray(0)

    # ------------------------------------------------------------------ #
    # API de desenho
    # ------------------------------------------------------------------ #
    def clear(self, r=0.0, g=0.0, b=0.0, a=1.0):
        self.gl.glClearColor(r, g, b, a)
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT)

    def _vtri(self, x1, y1, r1, g1, b1, a1,
              x2, y2, r2, g2, b2, a2,
              x3, y3, r3, g3, b3, a3):
        self.tris.append([(x1, y1, r1, g1, b1, a1),
                          (x2, y2, r2, g2, b2, a2),
                          (x3, y3, r3, g3, b3, a3)])

    def _quad(self, x1, y1, x2, y2, x3, y3, x4, y4, r, g, b, a):
        self._vtri(x1, y1, r, g, b, a, x2, y2, r, g, b, a, x3, y3, r, g, b, a)
        self._vtri(x1, y1, r, g, b, a, x3, y3, r, g, b, a, x4, y4, r, g, b, a)

    def rect(self, x, y, w, h, r, g, b, a=1.0):
        if w <= 0 or h <= 0:
            return
        self._quad(x, y, x + w, y, x + w, y + h, x, y + h, r, g, b, a)

    def point(self, x, y, radius, r, g, b, a=1.0, seg=10):
        if radius < 1.0:
            self.rect(x - 1, y - 1, 2, 2, r, g, b, a)
            return
        self.ellipse(x, y, radius, radius, r, g, b, a, seg)

    def ellipse(self, cx, cy, rx, ry, r, g, b, a=1.0, seg=32):
        if rx < 0.5 or ry < 0.5 or seg < 3:
            return
        for i in range(seg):
            t1 = 2.0 * math.pi * i / seg
            t2 = 2.0 * math.pi * (i + 1) / seg
            x1 = cx + rx * math.cos(t1)
            y1 = cy + ry * math.sin(t1)
            x2 = cx + rx * math.cos(t2)
            y2 = cy + ry * math.sin(t2)
            self._vtri(cx, cy, r, g, b, a, x1, y1, r, g, b, a, x2, y2, r, g, b, a)

    def ring_ellipse(self, cx, cy, rx_out, ry_out, rx_in, ry_in,
                     r, g, b, a=1.0, seg=32):
        """Aneis/borda de elipse: tubo de triangulos entre duas elipses."""
        if seg < 3:
            return
        for i in range(seg):
            t1 = 2.0 * math.pi * i / seg
            t2 = 2.0 * math.pi * (i + 1) / seg
            ax1 = cx + rx_out * math.cos(t1)
            ay1 = cy + ry_out * math.sin(t1)
            bx1 = cx + rx_in * math.cos(t1)
            by1 = cy + ry_in * math.sin(t1)
            ax2 = cx + rx_out * math.cos(t2)
            ay2 = cy + ry_out * math.sin(t2)
            bx2 = cx + rx_in * math.cos(t2)
            by2 = cy + ry_in * math.sin(t2)
            self._quad(ax1, ay1, ax2, ay2, bx2, by2, bx1, by1, r, g, b, a)

    def poly(self, pontos, r, g, b, a=1.0):
        """Poligono convexo (ventilador a partir do centroide)."""
        if len(pontos) < 3:
            return
        cx = sum(p[0] for p in pontos) / len(pontos)
        cy = sum(p[1] for p in pontos) / len(pontos)
        for i in range(len(pontos)):
            j = (i + 1) % len(pontos)
            x1, y1 = pontos[i]
            x2, y2 = pontos[j]
            self._vtri(cx, cy, r, g, b, a,
                       x1, y1, r, g, b, a, x2, y2, r, g, b, a)

    def thick_line(self, x1, y1, x2, y2, largura, r, g, b, a=1.0):
        """Segmento de linha com largura (quad bidimensional)."""
        dx = x2 - x1
        dy = y2 - y1
        comprimento = math.hypot(dx, dy)
        if comprimento < 0.0001:
            self.point(x1, y1, max(1.0, largura * 0.5), r, g, b, a)
            return
        nx = -dy / comprimento
        ny = dx / comprimento
        hw = largura * 0.5
        ax = x1 + nx * hw
        ay = y1 + ny * hw
        bx = x2 + nx * hw
        by = y2 + ny * hw
        cx = x2 - nx * hw
        cy = y2 - ny * hw
        dx2 = x1 - nx * hw
        dy2 = y1 - ny * hw
        self._quad(ax, ay, bx, by, cx, cy, dx2, dy2, r, g, b, a)

    def text(self, texto, x, y, scale, r, g, b, a=1.0, align='left'):
        """Renderiza texto na fonte bitmap 5x7.

        :param scale: pixels por coluna da fonte (1 = 5px/char).
        :param align: 'left', 'center' ou 'right' (relativo a x).
        """
        texto = str(texto).upper()
        total_w = (len(texto) * 6 - 1) * scale if texto else 0
        if align == 'center':
            x0 = x - total_w * 0.5
        elif align == 'right':
            x0 = x - total_w
        else:
            x0 = x
        for i, ch in enumerate(texto):
            glyph = FONT_5x7.get(ch)
            if glyph is None:
                glyph = FONT_5x7["?"]
            gx = x0 + i * 6 * scale
            for row, bits in enumerate(glyph):
                for col, px in enumerate(bits):
                    if px == '1':
                        self.rect(gx + col * scale, y + row * scale,
                                  scale, scale, r, g, b, a)

    # ------------------------------------------------------------------ #
    # Upload e desenho
    # ------------------------------------------------------------------ #
    def flush(self):
        gl = self.gl
        tri_vert = 0
        partes = []
        for t in self.tris:
            for (vx, vy, r, g, b, a) in t:
                ndc_x = (vx / self.w) * 2.0 - 1.0
                ndc_y = 1.0 - (vy / self.h) * 2.0
                partes.append(struct.pack('<2f4f', ndc_x, ndc_y, r, g, b, a))
                tri_vert += 1
        self.tris = []
        if tri_vert == 0:
            self._additive = False
            return
        dados = b''.join(partes)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(dados), dados, gl.GL_DYNAMIC_DRAW)
        gl.glBindVertexArray(self.vao)
        gl.glUseProgram(self.prog)
        gl.glEnable(gl.GL_BLEND)
        if self._additive:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        else:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, tri_vert)
        gl.glDisable(gl.GL_BLEND)
        gl.glUseProgram(0)
        gl.glBindVertexArray(0)
        self._additive = False

    def resize(self, w, h):
        self.w = float(w)
        self.h = float(h)
