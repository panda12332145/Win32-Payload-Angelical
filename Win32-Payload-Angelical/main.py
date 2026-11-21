#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu interativo do Win32-Payload-Angelical.

Permite escolher qual payload de efeito visual GDI executar, rodar todos em
sequencia, ou abrir o Anjo Trono (Ophanim) em modo dedicado.

Uso:
    python main.py            -> abre o menu interativo
    python main.py --list     -> lista os payloads e sai
    python main.py --angel    -> roda direto o Anjo Trono
    python main.py --all      -> roda todos em sequencia
    python main.py --fps 30   -> define o FPS (padrao 30)

ATENCAO: requer Windows + pywin32. Execute preferencialmente a partir da
raiz do projeto.
"""

import argparse
import sys


def _carregar_engine():
    """Importa o engine com mensagem amigavel caso nao esteja no Windows."""
    try:
        from src.engine import run_all, run_payload, list_payloads
        from src.payloads import ALL_PAYLOADS, OphanimAngelPayload
    except ImportError as e:
        print("[ERRO] Nao foi possivel importar o engine GDI.")
        print("       Este projeto usa pywin32 e SO funciona no Windows.")
        print("       Instale as dependencias com: pip install -r requirements.txt")
        print("       Detalhe: {}".format(e))
        sys.exit(1)
    return (run_all, run_payload, list_payloads, ALL_PAYLOADS,
            OphanimAngelPayload)


def menu_interativo(fps):
    (run_all, run_payload, list_payloads,
     ALL_PAYLOADS, OphanimAngelPayload) = _carregar_engine()

    while True:
        print("\n" + "=" * 54)
        print("   WIN32-PAYLOAD-ANGELICAL  -  Efeitos GDI de Horror")
        print("=" * 54)
        for linha in list_payloads():
            print("  " + linha)
        print("  [A] Rodar TODOS em sequencia")
        print("  [G] Anjo Trono (Ophanim) em modo dedicado")
        print("  [Q] Sair")
        print("-" * 54)
        print("  (ESC durante a execucao encerra o efeito atual)")

        escolha = input(">> Escolha uma opcao: ").strip().lower()

        if escolha in ("q", "quit", "sair"):
            print("Ate logo.")
            return
        if escolha in ("a", "all", "todos"):
            run_all(fps=fps)
            continue
        if escolha in ("g", "angel", "anjo"):
            print("[INFO] Invocando o Anjo Trono... (ESC para sair)")
            run_payload(OphanimAngelPayload(), fps=fps)
            continue

        # Tenta interpretar como indice numerico.
        try:
            idx = int(escolha)
        except ValueError:
            print("[AVISO] Opcao invalida.")
            continue
        if 0 <= idx < len(ALL_PAYLOADS):
            payload_cls = ALL_PAYLOADS[idx]
            nome = getattr(payload_cls, "name", payload_cls.__name__)
            print("[INFO] Executando '{}' ... (ESC para sair)".format(nome))
            run_payload(payload_cls(), fps=fps)
        else:
            print("[AVISO] Indice fora do intervalo.")


def main():
    ap = argparse.ArgumentParser(
        description="Win32-Payload-Angelical - efeitos GDI de horror/terror.")
    ap.add_argument("--list", action="store_true", help="lista os payloads e sai")
    ap.add_argument("--all", action="store_true", help="roda todos em sequencia")
    ap.add_argument("--angel", action="store_true",
                    help="roda o Anjo Trono (Ophanim) diretamente")
    ap.add_argument("--fps", type=int, default=30, help="quadros por segundo")
    args = ap.parse_args()

    (run_all, run_payload, list_payloads,
     ALL_PAYLOADS, OphanimAngelPayload) = _carregar_engine()

    if args.list:
        print("\n".join(list_payloads()))
        return
    if args.angel:
        print("[INFO] Invocando o Anjo Trono... (ESC para sair)")
        run_payload(OphanimAngelPayload(), fps=args.fps)
        return
    if args.all:
        run_all(fps=args.fps)
        return

    menu_interativo(args.fps)


if __name__ == "__main__":
    main()
