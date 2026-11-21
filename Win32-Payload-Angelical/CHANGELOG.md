# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

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
