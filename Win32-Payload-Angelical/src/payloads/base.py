# -*- coding: utf-8 -*-
"""Classe base para todos os payloads de efeitos visuais GDI.

Cada payload desenha diretamente sobre o Device Context (hdc) da área de
trabalho do Windows usando as APIs do pywin32 (win32gui / win32con / win32api).

Existem dois tipos de payload:
  * Sem estado  -> o metodo draw() desenha um quadro completo a cada chamada.
  * Com estado  -> o payload guarda atributos (ex.: angulos, fases de animacao)
                   que sao atualizados a cada quadro para gerar animacao fluida.
                   Esses payloads definem ``stateful = True``.
"""

import win32api


class Payload:
    """Classe base de todos os payloads de animacao.

    Subclasses devem implementar ``draw(self, hdc, w, h)``.
    """

    #: Nome amigavel exibido no menu interativo.
    name = "payload"

    #: Descricao curta do efeito.
    description = "Efeito visual GDI."

    #: Indica se o payload mantem estado entre quadros (animacao frame-a-frame).
    stateful = False

    def draw(self, hdc, w, h):
        """Desenha um quadro do efeito.

        :param hdc: handle do Device Context onde desenhar.
        :param w: largura da tela em pixels.
        :param h: altura da tela em pixels.
        """
        raise NotImplementedError("Subclasses devem implementar draw().")

    # ------------------------------------------------------------------ #
    # Utilitarios de cor compartilhados por varios payloads.
    # ------------------------------------------------------------------ #
    @staticmethod
    def rgb(r, g, b):
        """Atalho para win32api.RGB mantendo os canais dentro de 0..255."""
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return win32api.RGB(r, g, b)
