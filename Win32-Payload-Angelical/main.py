#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu interativo do Win32-Payload-Angelical.

Permite escolher qual payload de efeito visual executar, rodar todos em
sequencia, ou abrir o Anjo Trono (Ophanim) diretamente — em dois engines:

  * GL (3D)  -> engine OpenGL + GLFW (PyOpenGL): renderizacao real em 3D,
                anti-aliasing, blending com alpha (recomendado).
  * GDI (antigo) -> renderizacao GDI do Windows via pywin32.

Uso:
    python main.py                       # menu interativo (engine auto)
    python main.py --engine gl           # engine OpenGL
    python main.py --engine gdi          # engine GDI (antigo)
    python main.py --list                # lista os efeitos
    python main.py --angel               # abre direto o Anjo Trono
    python main.py --all                 # roda todos em sequencia
    python main.py --fps 60              # FPS (padrao: 60)
"""

import argparse
import sys


def _detectar_engine_gl():
    """True se PyOpenGL + glfw estiverem instalados e importaveis."""
    try:
        import glfw  # noqa: F401
        from OpenGL import GL  # noqa: F401
        return True
    except Exception:
        return False


def _resolve_engine(preferido):
    """auto -> GL se disponivel, senao gdi; gl -> GL (erro se indisponivel);
    gdi -> GDI (erro se pywin32 indisponivel)."""
    if preferido == "gdi":
        return "gdi"
    if preferido == "gl":
        if _detectar_engine_gl():
            return "gl"
        print("[AVISO] Engine OpenGL indisponivel (PyOpenGL/glfw ausentes).")
        print("        Instale: pip install -r requirements.txt")
        print("        Fallback: usando engine GDI.")
        return "gdi"
    # auto
    if _detectar_engine_gl():
        return "gl"
    print("[AVISO] OpenGL indisponivel (PyOpenGL/glfw ausentes).")
    print("        Usando engine GDI (antigo). Para o engine 3D:")
    print("        pip install -r requirements.txt")
    return "gdi"


def _carregar_engine(engine_nome):
    """Importa o engine escolhido de forma lazy com mensagens amigaveis."""
    if engine_nome == "gl":
        try:
            from src.gl_engine import run_gl_effect, run_all_gl, list_gl_effects
            from src.gl_effects import GL_EFFECTS
            return (run_gl_effect, run_all_gl, list_gl_effects, GL_EFFECTS, None)
        except ImportError as e:
            print("[ERRO] Nao foi possivel importar o engine OpenGL.")
            print("       Instale: pip install -r requirements.txt")
            print("       Detalhe: {}".format(e))
            sys.exit(1)
    else:
        try:
            from src.engine import run_all, run_payload, list_payloads
            from src.payloads import ALL_PAYLOADS, OphanimAngelPayload
            return (run_payload, run_all, list_payloads, ALL_PAYLOADS,
                    OphanimAngelPayload)
        except ImportError as e:
            print("[ERRO] Nao foi possivel importar o engine GDI.")
            print("       Este projeto usa pywin32 e SO funciona no Windows.")
            print("       Instale as dependencias com: pip install -r requirements.txt")
            print("       Detalhe: {}".format(e))
            sys.exit(1)


def menu_interativo(fps, engine_nome):
    (run_effect, run_all, list_effects, EFFECTS, ANGEL_GDI) = _carregar_engine(engine_nome)
    titulo_engine = "OpenGL (3D)" if engine_nome == "gl" else "GDI (antigo)"

    while True:
        print("\n" + "=" * 54)
        print("   WIN32-PAYLOAD-ANGELICAL  -  Efeitos de Horror")
        print("   Engine: " + titulo_engine)
        print("=" * 54)
        for linha in list_effects():
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
            try:
                run_all(fps=fps)
            except RuntimeError as e:
                print("[ERRO] Nao foi possivel abrir o efeito: {}".format(e))
            continue
        if escolha in ("g", "angel", "anjo"):
            try:
                if engine_nome == "gl":
                    from src.gl_effects import OphanimAngelGl
                    print("[INFO] Invocando o Anjo Trono (OpenGL 3D)... (ESC para sair)")
                    run_effect(OphanimAngelGl(), fps=fps)
                else:
                    print("[INFO] Invocando o Anjo Trono... (ESC para sair)")
                    run_effect(ANGEL_GDI(), fps=fps)
            except RuntimeError as e:
                print("[ERRO] Nao foi possivel abrir o efeito: {}".format(e))
            continue

        try:
            idx = int(escolha)
        except ValueError:
            print("[AVISO] Opcao invalida.")
            continue
        if 0 <= idx < len(EFFECTS):
            effect = EFFECTS[idx]()
            nome = getattr(effect, "name", effect.__class__.__name__)
            print("[INFO] Executando '{}' ... (ESC para sair)".format(nome))
            try:
                run_effect(effect, fps=fps)
            except RuntimeError as e:
                print("[ERRO] Nao foi possivel abrir o efeito: {}".format(e))
        else:
            print("[AVISO] Indice fora do intervalo.")


def main():
    ap = argparse.ArgumentParser(
        description="Win32-Payload-Angelical - efeitos visuais de horror.")
    ap.add_argument("--list", action="store_true", help="lista os efeitos e sai")
    ap.add_argument("--all", action="store_true", help="roda todos em sequencia")
    ap.add_argument("--angel", action="store_true",
                    help="roda o Anjo Trono (Ophanim) diretamente")
    ap.add_argument("--fps", type=int, default=60, help="quadros por segundo (padrao 60)")
    ap.add_argument("--engine", choices=("auto", "gl", "gdi"), default="auto",
                    help="engine de renderizacao (padrao: auto)")
    ap.add_argument("--gl-check", action="store_true",
                    help="Testa o engine OpenGL (janela + 5 quadros) e sai")
    args = ap.parse_args()

    if args.gl_check:
        from src.gl_engine import test_engine
        print("[INFO] Testando o engine OpenGL...")
        ok = test_engine()
        print("[RESULTADO] OpenGL:", "OK" if ok else "FALHOU")
        sys.exit(0 if ok else 1)

    engine_nome = _resolve_engine(args.engine)
    (run_effect, run_all, list_effects, EFFECTS, ANGEL_GDI) = _carregar_engine(engine_nome)

    if args.list:
        print("\n".join(list_effects()))
        return
    if args.angel:
        try:
            if engine_nome == "gl":
                from src.gl_effects import OphanimAngelGl
                print("[INFO] Invocando o Anjo Trono (OpenGL 3D)... (ESC para sair)")
                run_effect(OphanimAngelGl(), fps=args.fps)
            else:
                print("[INFO] Invocando o Anjo Trono... (ESC para sair)")
                run_effect(ANGEL_GDI(), fps=args.fps)
        except RuntimeError as e:
            print("[ERRO] Nao foi possivel abrir o efeito: {}".format(e))
            sys.exit(1)
        return
    if args.all:
        try:
            run_all(fps=args.fps)
        except RuntimeError as e:
            print("[ERRO] Nao foi possivel abrir o efeito: {}".format(e))
            sys.exit(1)
        return

    menu_interativo(args.fps, engine_nome)


if __name__ == "__main__":
    main()
