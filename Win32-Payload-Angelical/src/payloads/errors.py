# -*- coding: utf-8 -*-
"""Payloads de ERRO (tema: falha de sistema / corrupcao digital).

Contem:
  * BlueScreenPayload  -> tela azul da morte (BSOD) falsa.
  * ErrorDialogPayload -> caixas de dialogo de erro falsas espalhadas.
  * GlitchPayload      -> blocos coloridos aleatorios (glitch digital).
"""

import random

import win32con
import win32gui

from .base import Payload


class BlueScreenPayload(Payload):
    """Desenha uma Tela Azul da Morte (BSOD) falsa com texto de Stop Code."""

    name = "Tela Azul (BSOD)"
    description = "Simula a tela azul de erro critico do Windows."
    stateful = False

    _LINHAS = [
        ":(",
        "",
        "Seu PC encontrou um problema e precisa reiniciar.",
        "Apenas coletando algumas informacoes de erro e entao",
        "reiniciaremos para voce.",
        "",
        "0% concluido",
        "",
        "Codigo de parada: CRITICAL_PROCESS_DIED",
        "Falha: ophanim.sys",
    ]

    def draw(self, hdc, w, h):
        # Preenche o fundo com o azul caracteristico do BSOD (#0078D7).
        brush = win32gui.CreateSolidBrush(self.rgb(0, 120, 215))
        win32gui.FillRect(hdc, (0, 0, w, h), brush)
        win32gui.DeleteObject(brush)

        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        win32gui.SetTextColor(hdc, self.rgb(255, 255, 255))

        margem_x = int(w * 0.12)
        y = int(h * 0.18)

        # Fonte grande para o ":(" e fonte menor para o corpo do texto.
        fonte_grande = win32gui.CreateFont(
            -int(h * 0.12), 0, 0, 0, win32con.FW_NORMAL,
            0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")
        fonte_corpo = win32gui.CreateFont(
            -int(h * 0.028), 0, 0, 0, win32con.FW_NORMAL,
            0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")

        for i, linha in enumerate(self._LINHAS):
            if i == 0:
                old = win32gui.SelectObject(hdc, fonte_grande)
                win32gui.TextOut(hdc, margem_x, y, linha)
                win32gui.SelectObject(hdc, old)
                y += int(h * 0.16)
            else:
                old = win32gui.SelectObject(hdc, fonte_corpo)
                win32gui.TextOut(hdc, margem_x, y, linha)
                win32gui.SelectObject(hdc, old)
                y += int(h * 0.045)

        win32gui.DeleteObject(fonte_grande)
        win32gui.DeleteObject(fonte_corpo)


class ErrorDialogPayload(Payload):
    """Desenha varias caixas de dialogo de erro falsas em posicoes aleatorias."""

    name = "Dialogos de Erro"
    description = "Enxame de caixas de erro falsas do Windows."
    stateful = False

    _TITULOS = ["ERRO CRITICO", "FALHA FATAL", "SYSTEM32 CORROMPIDO",
                "ACESSO NEGADO", "KERNEL PANIC"]
    _MENSAGENS = ["O processo ophanim.exe parou de responder.",
                  "Memoria nao pode ser 'read'. Endereco 0x00EDEN.",
                  "Um erro desconhecido ocorreu (0xDEAD).",
                  "Arquivo corrompido: soul.dll",
                  "Operacao invalida detectada."]

    def draw(self, hdc, w, h):
        dlg_w, dlg_h = 320, 140
        for _ in range(12):
            x = random.randint(0, max(w - dlg_w, 1))
            y = random.randint(0, max(h - dlg_h, 1))

            # Corpo cinza da caixa de dialogo.
            corpo = win32gui.CreateSolidBrush(self.rgb(240, 240, 240))
            win32gui.FillRect(hdc, (x, y, x + dlg_w, y + dlg_h), corpo)
            win32gui.DeleteObject(corpo)

            # Barra de titulo azul.
            titulo_brush = win32gui.CreateSolidBrush(self.rgb(200, 30, 30))
            win32gui.FillRect(hdc, (x, y, x + dlg_w, y + 28), titulo_brush)
            win32gui.DeleteObject(titulo_brush)

            # Borda da caixa.
            pen = win32gui.CreatePen(win32con.PS_SOLID, 1, self.rgb(80, 80, 80))
            old_pen = win32gui.SelectObject(hdc, pen)
            nb = win32gui.GetStockObject(win32con.NULL_BRUSH)
            old_brush = win32gui.SelectObject(hdc, nb)
            win32gui.Rectangle(hdc, x, y, x + dlg_w, y + dlg_h)
            win32gui.SelectObject(hdc, old_brush)
            win32gui.SelectObject(hdc, old_pen)
            win32gui.DeleteObject(pen)

            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)

            # Texto do titulo (branco).
            fonte_t = win32gui.CreateFont(
                -15, 0, 0, 0, win32con.FW_BOLD, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            old_f = win32gui.SelectObject(hdc, fonte_t)
            win32gui.SetTextColor(hdc, self.rgb(255, 255, 255))
            win32gui.TextOut(hdc, x + 8, y + 6, random.choice(self._TITULOS))
            win32gui.SelectObject(hdc, old_f)
            win32gui.DeleteObject(fonte_t)

            # Texto da mensagem (preto).
            fonte_m = win32gui.CreateFont(
                -14, 0, 0, 0, win32con.FW_NORMAL, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            old_f = win32gui.SelectObject(hdc, fonte_m)
            win32gui.SetTextColor(hdc, self.rgb(20, 20, 20))
            win32gui.TextOut(hdc, x + 12, y + 50, random.choice(self._MENSAGENS))
            win32gui.SelectObject(hdc, old_f)
            win32gui.DeleteObject(fonte_m)

            # Botao OK.
            bx1, by1 = x + dlg_w - 90, y + dlg_h - 36
            bx2, by2 = x + dlg_w - 20, y + dlg_h - 10
            botao = win32gui.CreateSolidBrush(self.rgb(210, 210, 210))
            win32gui.FillRect(hdc, (bx1, by1, bx2, by2), botao)
            win32gui.DeleteObject(botao)
            fonte_b = win32gui.CreateFont(
                -13, 0, 0, 0, win32con.FW_NORMAL, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
            old_f = win32gui.SelectObject(hdc, fonte_b)
            win32gui.SetTextColor(hdc, self.rgb(0, 0, 0))
            win32gui.TextOut(hdc, bx1 + 26, by1 + 5, "OK")
            win32gui.SelectObject(hdc, old_f)
            win32gui.DeleteObject(fonte_b)


class GlitchPayload(Payload):
    """Blocos RGB aleatorios criando um efeito de glitch / corrupcao de video."""

    name = "Glitch Digital"
    description = "Blocos coloridos aleatorios simulando corrupcao de video."
    stateful = False

    def draw(self, hdc, w, h):
        for _ in range(400):
            bw = random.randint(20, 240)
            bh = random.randint(4, 40)
            x = random.randint(0, max(w - bw, 1))
            y = random.randint(0, max(h - bh, 1))

            # Mistura de blocos de cor pura (R, G, B, ciano, magenta) e ruido.
            escolha = random.random()
            if escolha < 0.25:
                cor = self.rgb(255, 0, 0)
            elif escolha < 0.5:
                cor = self.rgb(0, 255, 0)
            elif escolha < 0.7:
                cor = self.rgb(0, 0, 255)
            elif escolha < 0.85:
                cor = self.rgb(0, 0, 0)
            else:
                cor = self.rgb(random.randint(0, 255),
                               random.randint(0, 255),
                               random.randint(0, 255))
            brush = win32gui.CreateSolidBrush(cor)
            win32gui.FillRect(hdc, (x, y, x + bw, y + bh), brush)
            win32gui.DeleteObject(brush)
