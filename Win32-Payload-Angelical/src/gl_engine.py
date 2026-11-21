# -*- coding: utf-8 -*-
"""Motor OpenGL do Win32-Payload-Angelical.

Renderiza os efeitos 3D em uma janela borderless maximizada (fullscreen-like)
usando GLFW + PyOpenGL. O engine mantem a estrutura do motor GDI (mesma API:
``run_gl_effect`` / ``run_all_gl`` / ``list_gl_effects``), mas a renderizacao
e feita em GPU com geometria triangularizada, blending com alpha e MSAA.

Uso:
    python main.py --engine gl --angel

Requer ``PyOpenGL`` e ``glfw`` (ver requirements.txt).
"""

import time


def _carregar_glfw():
    try:
        import glfw
    except ImportError:
        raise RuntimeError(
            "OpenGL indisponivel: instale com 'pip install PyOpenGL glfw' "
            "para usar o engine 3D (ou use --engine gdi).")
    return glfw


def _gl_ctx():
    try:
        from OpenGL import GL
    except ImportError:
        raise RuntimeError(
            "PyOpenGL nao esta instalado: 'pip install PyOpenGL' "
            "(ou use --engine gdi).")
    return GL


def _criar_janela(glfw, titulo, w, h):
    """Cria uma janela cheia de tela. Retorna (window, w, h).

    Estrategia: passa o monitor primario a create_window (GLFW cria uma
    janela fullscreen sem decoracoes). Se isso falhar, cai para uma janela
    maximizada borderless. Retorna tamanhos de framebuffer reais.
    """
    if not glfw.init():
        raise RuntimeError(
            "glfw nao conseguiu inicializar (sem display?): verifique se ha "
            "um display ativo e se o GLFW esta instalado.")

    monitor = None
    fw, fh = w, h
    try:
        monitor = glfw.get_primary_monitor()
    except Exception:
        monitor = None

    if monitor:
        try:
            xpos, ypos, fw, fh = glfw.get_monitor_workarea(monitor)
            if fw < 16 or fh < 16:
                fw, fh = w, h
        except Exception:
            pass

    # Hints para contexto OpenGL core profile (necessario para #version 330 core).
    def _set_hints(major, minor, core=True):
        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
            if core and hasattr(glfw, "OPENGL_PROFILE"):
                glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        except Exception:
            pass
        try:
            glfw.window_hint(glfw.SAMPLES, 4)
        except Exception:
            pass

    def _create(hint):
        hint()
        monitors = (monitor, None) if monitor else (None,)
        for mon in monitors:
            try:
                win = glfw.create_window(fw, fh, titulo, mon, None)
            except Exception:
                win = None
            if win:
                return win, mon
        return None, None

    window = None
    used_monitor = None
    for (major, minor, core) in [(3, 3, True), (3, 2, True), (3, 1, True), (3, 1, False), (None, None, False)]:
        if major is None:
            def hint():
                pass
        else:
            def hint():
                _set_hints(major, minor, core)
        try:
            window, used_monitor = _create(hint)
        except Exception:
            window = None
        if window:
            break
    if not window:
        glfw.terminate()
        raise RuntimeError(
            "glfw.create_window falhou em todos os perfis tentados. "
            "Verifique se ha display ativo e se o GLFW esta instalado.")

    glfw.make_context_current(window)

    if not used_monitor:
        try:
            glfw.maximize_window(window)
        except Exception:
            pass

    try:
        glfw.show_window(window)
    except Exception:
        pass

    try:
        fw2, fh2 = glfw.get_framebuffer_size(window)
        if fw2 >= 16 and fh2 >= 16:
            fw, fh = fw2, fh2
    except Exception:
        pass
    return window, fw, fh


def _tecla_esc(glfw, window):
    """True se ESC estiver pressionado neste quadro (glfw.PRESS)."""
    try:
        return int(glfw.get_key(window, glfw.KEY_ESCAPE)) == int(glfw.PRESS)
    except Exception:
        return False


class GlEngine(object):
    """Motor OpenGL: janela, renderer e loop de desenho."""

    def __init__(self, fps=60):
        self.fps = max(1, fps)
        self.glfw = _carregar_glfw()
        self.gl = None
        self.window = None
        self.renderer = None
        self.w = 0
        self.h = 0
        self._t0 = None
        self._prev = None

    def iniciar(self, titulo, w=1280, h=720):
        self.window, self.w, self.h = _criar_janela(self.glfw, titulo, w, h)
        # Importar OpenGL SO apos criar o contexto (recipe oficial PyOpenGL).
        self.gl = _gl_ctx()
        from .gl_effects.renderer import Renderer
        self.renderer = Renderer(self.gl, self.w, self.h)
        self._t0 = time.time()
        self._prev = self._t0

    def encerrar(self):
        if self.window is not None:
            try:
                self.glfw.destroy_window(self.window)
            except Exception:
                pass
            self.window = None
        try:
            self.glfw.terminate()
        except Exception:
            pass
        self.renderer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.encerrar()

    def _frame(self, effect, duracao=None):
        """Loop principal. Retorna True se ESC foi pressionado."""
        glfw = self.glfw
        gl = self.gl
        window = self.window
        renderer = self.renderer

        delay = 1.0 / self.fps
        inicio = time.time()
        t_inicio = self._t0 or inicio
        esc = False

        try:
            while not glfw.window_should_close(window):
                agora = time.time()
                dt = min(0.05, agora - (self._prev or agora))
                self._prev = agora
                t = agora - t_inicio

                try:
                    fw, fh = glfw.get_framebuffer_size(window)
                except Exception:
                    fw, fh = self.w, self.h
                if fw < 16 or fh < 16:
                    fw, fh = self.w, self.h
                self.w, self.h = fw, fh
                renderer.resize(fw, fh)
                gl.glViewport(0, 0, fw, fh)

                effect.update(dt, fw, fh, t)
                effect.draw(renderer, fw, fh, t)

                # Atalho de "ESC para sair" (sempre visivel, discreto)
                renderer.text("ESC PARA SAIR",
                              fw * 0.5, fh - 20, 2,
                              0.55, 0.55, 0.55, 0.40, align='center')
                renderer.flush()

                glfw.swap_buffers(window)
                glfw.poll_events()

                if _tecla_esc(glfw, window):
                    esc = True
                    break
                if duracao is not None and (time.time() - inicio) >= duracao:
                    break

                time.sleep(max(0.0, delay - (time.time() - agora)))
        except KeyboardInterrupt:
            esc = True
            print("\n[INFO] Encerrado pelo usuario (Ctrl+C).")

        return esc

    def run(self, effect, duracao=None):
        """Executa um efeito. Retorna True se ESC foi pressionado."""
        self._prev = None
        return self._frame(effect, duracao=duracao)


def _window_title(nome):
    return "Win32-Payload-Angelical  |  " + str(nome)


def run_gl_effect(effect_cls, fps=60, duracao=None):
    """Executa um efeito OpenGL ate ESC/Ctrl+C/duracao.

    :param effect_cls: classe de efeito OpenGL (ou instancia).
    """
    if isinstance(effect_cls, type):
        effect = effect_cls()
    else:
        effect = effect_cls
    with GlEngine(fps=fps) as engine:
        engine.iniciar(_window_title(getattr(effect, "name", "Efeito")))
        engine.run(effect, duracao=duracao)


def list_gl_effects():
    """Retorna a lista de nomes amigaveis dos efeitos registrados."""
    from .gl_effects import GL_EFFECTS
    nomes = []
    for i, cls in enumerate(GL_EFFECTS):
        nome = getattr(cls, "name", cls.__name__)
        nomes.append("[{}] {}".format(i, nome))
    return nomes


def run_all_gl(fps=60, tempo_por_payload=10.0):
    """Executa todos os efeitos em sequencia, cada um por alguns segundos."""
    from .gl_effects import GL_EFFECTS
    for cls in GL_EFFECTS:
        nome = getattr(cls, "name", cls.__name__)
        print("[INFO] Executando: {}".format(nome))
        esc = False
        with GlEngine(fps=fps) as engine:
            engine.iniciar(_window_title(nome))
            effect = cls()
            esc = engine.run(effect, duracao=tempo_por_payload)
        if esc:
            break
    try:
        print("[INFO] Engine finalizado.")
    finally:
        pass

def test_engine():
    """Teste rapido do engine OpenGL (janela + 5 quadros do Anjo Trono).

    Retorna True se o engine criou janela, renderizou e encerrou com sucesso.
    """
    try:
        from .gl_effects import OphanimAngelGl
        with GlEngine(fps=60) as engine:
            engine.iniciar("Win32-Payload-Angelical - teste GL")
            effect = OphanimAngelGl()
            import time as _t
            inicio = _t.time()
            quadros = 0
            while quadros < 5 and (_t.time() - inicio) < 1.0:
                agora = _t.time()
                dt = min(0.05, agora - (engine._prev or agora))
                engine._prev = agora
                t = agora - engine._t0
                fw, fh = engine.glfw.get_framebuffer_size(engine.window)
                engine.renderer.resize(fw, fh)
                engine.gl.glViewport(0, 0, fw, fh)
                effect.update(dt, fw, fh, t)
                effect.draw(engine.renderer, fw, fh, t)
                engine.renderer.flush()
                engine.glfw.swap_buffers(engine.window)
                engine.glfw.poll_events()
                quadros += 1
            engine.encerrar()
        return True
    except Exception as e:
        print("[ERRO] Engine GL falhou: {}".format(e))
        return False
