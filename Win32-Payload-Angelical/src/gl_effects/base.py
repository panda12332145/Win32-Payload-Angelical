# -*- coding: utf-8 -*-
"""Classe base dos efeitos OpenGL.

Cada efeito constroi geometria a cada frame com os primitivos do ``Renderer``
(rect/ellipse/poly/thick_line/text) e deixa o engine cuidar de janela, ESC,
FPS e timing. Os efeitos sao dt-based (tempo real), nao frame-based, para
fluir de forma consistente a qualquer FPS.
"""

import math
import random


class GlEffect(object):
    """Base para todos os efeitos OpenGL."""

    name = "Efeito"
    description = "Efeito OpenGL."

    def __init__(self):
        self._iniciado = False

    # ------------------------------------------------------------------ #
    # Estrutura esperada nas subclasses
    # ------------------------------------------------------------------ #
    def _iniciar(self, w, h):
        """Chamada uma unica vez no primeiro ``update``/``draw``."""

    def update(self, dt, w, h, t):
        """Avanca o estado do efeito (dt em segundos, t em segundos desde
        o inicio da execucao, w/h em pixels)."""

    def draw(self, r, w, h, t):
        """Constrói a geometria do frame no renderer ``r``."""

    # ------------------------------------------------------------------ #
    # Conveniencias
    # ------------------------------------------------------------------ #
    def _ok(self, w, h):
        return w >= 16 and h >= 16

    @staticmethod
    def rgb(r, g, b):
        return (max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)))

    @staticmethod
    def rand_range(a, b):
        return random.uniform(a, b)

    @staticmethod
    def rand_int(a, b):
        return random.randint(a, b)
