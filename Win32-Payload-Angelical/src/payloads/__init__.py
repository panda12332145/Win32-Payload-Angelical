# -*- coding: utf-8 -*-
"""Pacote de payloads de efeitos visuais GDI (tema horror/terror angelical).

Exporta todos os payloads e a lista ``ALL_PAYLOADS`` usada pelo engine.
"""

from .base import Payload
from .errors import BlueScreenPayload, ErrorDialogPayload, GlitchPayload
from .terror import (
    BloodDropPayload,
    CracksPayload,
    ShadowFigurePayload,
    SkullPayload,
    DarknessPayload,
)
from .eyes import EyesPayload
from .angel import OphanimAngelPayload

# Registro de todos os payloads disponiveis (ordem do menu).
ALL_PAYLOADS = [
    # --- Erros ---
    BlueScreenPayload,
    ErrorDialogPayload,
    GlitchPayload,
    # --- Terror ---
    BloodDropPayload,
    CracksPayload,
    ShadowFigurePayload,
    SkullPayload,
    DarknessPayload,
    # --- Olhos ---
    EyesPayload,
    # --- Anjo principal ---
    OphanimAngelPayload,
]

__all__ = [
    "Payload",
    "BlueScreenPayload",
    "ErrorDialogPayload",
    "GlitchPayload",
    "BloodDropPayload",
    "CracksPayload",
    "ShadowFigurePayload",
    "SkullPayload",
    "DarknessPayload",
    "EyesPayload",
    "OphanimAngelPayload",
    "ALL_PAYLOADS",
]
