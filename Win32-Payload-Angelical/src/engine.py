# -*- coding: utf-8 -*-
"""Motor de animacao (engine) do Win32-Payload-Angelical.

Responsavel por obter o Device Context da area de trabalho e chamar o metodo
``draw()`` dos payloads em loop, controlando o FPS. Suporta:

  * Payloads SEM estado  -> uma nova instancia e desenhada a cada quadro.
  * Payloads COM estado  -> a mesma instancia e mantida e desenhada quadro a
                            quadro (animacao fluida: aneis girando, asas
                            batendo, olhos piscando, etc.).

Controles:
  * ESC  -> encerra o loop (via GetAsyncKeyState).
  * Ctrl+C -> tambem encerra.

ATENCAO: este motor usa a API GDI do Windows (pywin32) e so funciona no
Windows. Em outros sistemas operacionais o import de win32gui falhara.
"""

import time

import win32api
import win32con
import win32gui

from .payloads import ALL_PAYLOADS


def list_payloads():
    """Retorna a lista de nomes amigaveis dos payloads registrados."""
    nomes = []
    for i, PayloadClass in enumerate(ALL_PAYLOADS):
        nome = getattr(PayloadClass, "name", PayloadClass.__name__)
        nomes.append("[{}] {}".format(i, nome))
    return nomes


def _tela():
    """Retorna (hwnd da area de trabalho, largura, altura)."""
    w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    hwnd = win32gui.GetDesktopWindow()
    return hwnd, w, h


def _esc_pressionado():
    """True se a tecla ESC estiver pressionada."""
    # 0x1B = VK_ESCAPE. O bit 0x8000 indica tecla pressionada agora.
    return bool(win32api.GetAsyncKeyState(0x1B) & 0x8000)


def run_payload(payload, fps=30, duracao=None):
    """Executa UM payload em loop (frame a frame) ate ESC/Ctrl+C/duracao.

    :param payload: instancia de Payload (ou classe; sera instanciada).
    :param fps: quadros por segundo desejados.
    :param duracao: tempo maximo em segundos (None = indefinido).
    """
    if isinstance(payload, type):
        payload = payload()

    hwnd, w, h = _tela()
    delay = 1.0 / max(1, fps)
    inicio = time.time()

    try:
        while True:
            hdc = win32gui.GetDC(hwnd)
            try:
                payload.draw(hdc, w, h)
            finally:
                win32gui.ReleaseDC(hwnd, hdc)

            if _esc_pressionado():
                print("\n[INFO] ESC pressionado. Encerrando payload.")
                break
            if duracao is not None and (time.time() - inicio) >= duracao:
                break
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n[INFO] Encerrado pelo usuario (Ctrl+C).")


def run_all(fps=30, tempo_por_payload=8.0):
    """Cicla por TODOS os payloads em sequencia, cada um por alguns segundos.

    :param fps: quadros por segundo.
    :param tempo_por_payload: segundos que cada payload fica em cena.
    """
    hwnd, w, h = _tela()
    delay = 1.0 / max(1, fps)

    try:
        for PayloadClass in ALL_PAYLOADS:
            payload = PayloadClass()
            nome = getattr(PayloadClass, "name", PayloadClass.__name__)
            print("[INFO] Executando: {}".format(nome))
            inicio = time.time()
            while (time.time() - inicio) < tempo_por_payload:
                hdc = win32gui.GetDC(hwnd)
                try:
                    payload.draw(hdc, w, h)
                finally:
                    win32gui.ReleaseDC(hwnd, hdc)
                if _esc_pressionado():
                    print("\n[INFO] ESC pressionado. Encerrando.")
                    return
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\n[INFO] Encerrado pelo usuario (Ctrl+C).")
    finally:
        print("[INFO] Engine finalizado.")


if __name__ == "__main__":
    run_all()
