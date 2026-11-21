# -*- coding: utf-8 -*-
"""Utilitario de fontes GDI (pywin32).

O pywin32 NAO exporta ``win32gui.CreateFont`` — essa API nao existe no modulo
(a causa do ``AttributeError: module 'win32gui' has no attribute 'CreateFont'``
e reportado pelo usuario). O caminho correto e o par
``win32gui.LOGFONT`` + ``win32gui.CreateFontIndirect``, que e exatamente o que
usam os exemplos oficiais do pywin32.

Este modulo centraliza a criacao de fontes com fallback:
  1. ``win32gui.LOGFONT`` + ``win32gui.CreateFontIndirect`` (caminho principal).
  2. ``win32gui.CreateFont`` (se existir, em alguma versao futura).
  3. Fonte stock (``GetStockObject(SYSTEM_FONT)``) — sempre existe.

As fontes sao cacheadas por (altura, peso, face) para nao criar/excluir
objetos a cada quadro (que seria lento e pode vazar memoria).
"""

import win32con
import win32gui

# Cache de fontes criadas neste processo (chave: (altura, peso, face)).
_cache = {}


def criar_fonte(altura=-20, peso=win32con.FW_NORMAL, face="Segoe UI",
                italic=False):
    """Cria (ou retorna em cache) uma fonte GDI.

    :param altura: altura em pixels; valores negativos usam o tamanho
        absoluto como altura de referencia (convencao GDI). Ex: -20.
    :param peso: peso da fonte (ex.: ``win32con.FW_NORMAL`` / ``FW_BOLD``).
    :param face: nome da fonte (ex.: "Segoe UI", "Arial").
    :param italic: negrito/itlico.
    :return: handle de fonte (HGDIOBJ) pronto para ``SelectObject``.
    """
    chave = (int(altura), int(peso), str(face), bool(italic))
    fonte = _cache.get(chave)
    if fonte is not None:
        return fonte

    handle = None

    # 1) Caminho oficial: LOGFONT + CreateFontIndirect (usado pelos exemplos
    #    do pywin32).
    try:
        lf = win32gui.LOGFONT()
        lf.lfHeight = int(altura)
        lf.lfWidth = 0
        lf.lfEscapement = 0
        lf.lfOrientation = 0
        lf.lfWeight = int(peso)
        lf.lfItalic = 1 if italic else 0
        lf.lfUnderline = 0
        lf.lfStrikeOut = 0
        lf.lfCharSet = win32con.ANSI_CHARSET
        lf.lfOutPrecision = win32con.OUT_DEFAULT_PRECIS
        lf.lfClipPrecision = win32con.CLIP_DEFAULT_PRECIS
        lf.lfQuality = win32con.PROOF_QUALITY
        lf.lfPitchAndFamily = win32con.DEFAULT_PITCH
        try:
            # Alguns pywin32 rejeitam face names longos; silence e segue.
            lf.lfFaceName = str(face)[:31]
        except Exception:
            pass
        handle = win32gui.CreateFontIndirect(lf)
    except Exception:
        handle = None

    # 2) Fallback para CreateFont se esse modulo expor (versao antiga/diferente).
    if handle is None:
        try:
            if hasattr(win32gui, "CreateFont"):
                handle = win32gui.CreateFont(
                    int(altura), 0, 0, 0, int(peso),
                    1 if italic else 0, 0, 0,
                    win32con.ANSI_CHARSET,
                    win32con.OUT_DEFAULT_PRECIS,
                    win32con.CLIP_DEFAULT_PRECIS,
                    win32con.PROOF_QUALITY,
                    win32con.DEFAULT_PITCH,
                    str(face))
        except Exception:
            handle = None

    # 3) Ultimo recurso: fonte stock do sistema (sempre existe).
    if handle is None:
        try:
            handle = win32gui.GetStockObject(win32con.SYSTEM_FONT)
        except Exception:
            handle = None

    if handle is None:
        # Sem fontes nadde? Pelo menos devolve None e deixa o chamador seguir
        # com a fonte padrao do DC (nada quebraria, nada renderizaria).
        return None

    _cache[chave] = handle
    return handle


def deletar_fonte(fonte):
    """Deleta uma fonte GDI criada por ``criar_fonte`` (se nao for cacheada).

    Fonts cacheadas sao intencionalmente mantidas viva; esta funcao apenas
    deleta fontes que o chamador criou manualmente.
    """
    if fonte is None:
        return
    try:
        win32gui.DeleteObject(fonte)
    except Exception:
        pass
