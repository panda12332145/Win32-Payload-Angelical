# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

## [1.1.0] - 2026-11-21

### Adicionado
- **Engine OpenGL 3D** (`src/gl_engine.py` + `src/gl_effects/`): janela
  borderless maximizada (GLFW + PyOpenGL) com MSAA (4x), blending alpha,
  geometria triangularizada com mistura aditiva para glow, fonte bitmap 5x7
  para texto sagrado e FPS configuravel.
- Efeitos OpenGL prontos: **Anjo Trono (Ophanim)** (3 aneis 3D rotacionando
  com olhos, olho central piscando, asas batendo, fogo e poeira, brilho
  pulsante), **Olhos Vigilantes**, **Sangue Escorrendo**, **Rachaduras**,
  **Figura Sombria**, **Cranios**, **Escuridao**, **Glitch Digital**.
- `main.py`: nova flag `--engine {auto,gl,gdi}` (auto detecta OpenGL e faz
  fallback para GDI). Menu agora mostra o engine ativo; efeitos GL e GDI
  sao selecionaveis.
- Constantes de fonte GDI via `src/payloads/fonts.py`, com cache e fallback
  (`CreateFontIndirect` + `LOGFONT` e, se faltar, stock font).
- `.gitignore` (remove cache de python do git).

### Corrigido
- **Erro fatal `AttributeError: module 'win32gui' has no attribute 'CreateFont'`**
  nos payloads `errors.py` e `angel.py` (a funcao nao existe no pywin32).
  Agora usa `LOGFONT` + `CreateFontIndirect` (caminho oficial) com cache.
- `fonts.py` nao deleta fontes cacheadas a cada quadro (economiza memoria).

### Alterado
- `requirements.txt`: adicionado `PyOpenGL` e `glfw` (modo GL).
- README reescrito para refletir o engine OpenGL.

---

## [1.0.0] - 2026-11-21

### Adicionado
- Estrutura inicial do projeto `Win32-Payload-Angelical`, inspirado no
  `Win32-Payload-Engine`.
- `src/payloads/base.py` — classe base `Payload` com utilitário de cor e
  suporte a payloads com estado (`stateful`).
- `src/engine.py` — motor de animação com controle de FPS, encerramento por
  ESC/Ctrl+C e suporte a payloads stateful e stateless (`run_payload`, `run_all`).
- **Payloads de erro** (`errors.py`): `BlueScreenPayload`, `ErrorDialogPayload`,
  `GlitchPayload`.
- **Payloads de terror** (`terror.py`): `BloodDropPayload`, `CracksPayload`,
  `ShadowFigurePayload`, `SkullPayload`, `DarknessPayload`.
- **Payload de olhos** (`eyes.py`): `EyesPayload` com 15–25 olhos piscando
  independentemente, íris dourada/vermelha, pupilas que acompanham o centro e
  veias vermelhas.
- **Payload principal** (`angel.py`): `OphanimAngelPayload` — Anjo Trono bíblico
  animado com 3 anéis girando em rotação 3D/perspectiva cobertos de olhos, olho
  central piscando, asas batendo em `Polygon`, partículas de fogo, brilho
  pulsante e texto sagrado flutuante.
- `main.py` — menu interativo e CLI (`--list`, `--all`, `--angel`, `--fps`).
- `README.md` com documentação completa em português.
- `requirements.txt` (apenas `pywin32`).
