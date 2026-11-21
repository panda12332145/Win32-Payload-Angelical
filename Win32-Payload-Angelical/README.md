# Win32-Payload-Angelical 👁️‍🗨️🔥

> Motor de efeitos visuais para Windows com tema de **horror / terror angelical**.
> Dois engines: **OpenGL 3D** (recomendado, real em GPU) e **GDI** (legado, via pywin32).

---

## ⚠️ Aviso importante

- Este projeto é **educacional**, voltado ao aprendizado de computação gráfica (OpenGL / GDI).
- Os efeitos são **puramente visuais** e **temporários**: desenham na tela, mas
  não modificam arquivos, não persistem após o fechamento e não possuem qualquer
  capacidade ofensiva. Pressione **ESC** (ou **Ctrl+C**) para encerrar — a tela
  se recompõe normalmente.
- Funciona **no Windows** (via pywin32/GDI) e em plataformas com OpenGL (GL).

---

## 📦 Instalação

```bash
# No Windows, com Python 3.8+
git clone https://github.com/panda12332145/Win32-Payload-Angelical.git
cd Win32-Payload-Angelical
pip install -r requirements.txt
```

Dependências:
- `pywin32` — modo GDI (antigo).
- `PyOpenGL` + `glfw` — modo OpenGL (3D, recomendado).

---

## ▶️ Como usar

```bash
python main.py                  # menu interativo (auto: GL)
python main.py --engine gl       # engine OpenGL 3D
python main.py --engine gdi      # engine GDI (antigo)
python main.py --list            # lista os efeitos
python main.py --angel           # abre direto o Anjo Trono (Ophanim)
python main.py --all             # roda todos em sequência
python main.py --fps 60          # FPS (padrão: 60)
```

Durante a execução, pressione **ESC** (ou **Ctrl+C**) para encerrar o efeito atual.

---

## 🎭 Efeitos disponíveis

### OpenGL 3D (recomendado)
| Efeito | Descrição |
|---|---|
| `OphanimAngelGl` | **Anjo Trono bíblico completo e animado em 3D** — 3 anéis girando com olhos, olho central piscando, asas batendo, fogo e brilho pulsante, texto sagrado. |
| `EyesGl` | Olhos vigiados com piscar independente, iris dourada/vermelha, pupila acompanhando o centro. |
| `BloodDropGl` | Gotas de sangue com gravidade e acúmulo no fundo. |
| `CracksGl` | Rachaduras se espalhando e bifurcando. |
| `ShadowFigureGl` | Silhueta humanoide que aparece e some em fade, com olhos vermelhos. |
| `SkullGl` | Crânios fantasmagoricos com halo vermelho. |
| `DarknessGl` | Vinheta de escuridão pulsante com estrelas distantes. |
| `GlitchGl` | Corrupção de vídeo: blocos coloridos, cortes e jitter. |

### GDI (antigo, mantido para compatibilidade)
Todos os efeitos acima também existem no modo GDI (`--engine gdi`), além de
`BlueScreenPayload` e `ErrorDialogPayload` (telas de erro/diálogos falsos estilo Windows).

---

## 😇 O Anjo Trono (Ophanim) — engine OpenGL 3D

Recriação do anjo biblico (Ezequiel 1 e 10):

- **3 anéis concêntricos** girando em velocidades/direções diferentes, usando
  **rotação 3D + projeção em perspectiva** (`math_3d.py`), cada um coberto de olhos.
- **Olho central gigante** com iris dourada, pupila vermelho-sangue e piscar dramático.
- **Duas asas simétricas** com 6 penas cada, batendo em onda senoidal.
- **Partículas de fogo** subindo ao fundo + poeira dourada flutuante.
- **Brilho quente pulsante** com mistura aditiva (glow real).
- **Texto sagrado** na fonte bitmap ("KADOSH KADOSH KADOSH" / "SANTO SANTO SANTO").
- **Poeira dourada** + vinheta suave para profundidade.

---

## 🧱 Estrutura do projeto

```
Win32-Payload-Angelical/
├── main.py                     # menu interativo / CLI
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── src/
    ├── __init__.py
    ├── engine.py               # loop de animação GDI (FPS, ESC)
    ├── gl_engine.py            # loop de animação OpenGL (janela, ESC, FPS)
    ├── gl_effects/             # effects 3D em OpenGL
    │   ├── __init__.py         # registry GL_EFFECTS
    │   ├── base.py             # GlEffect (base dt-based)
    │   ├── renderer.py         # renderer (shaders, geometria, texto bitmap)
    │   ├── font.py             # fonte bitmap 5x7
    │   ├── math_3d.py          # rotação/projeção 3D
    │   ├── angel.py            # Anjo Trono (Ophanim)
    │   ├── eyes.py, blood.py, cracks.py, darkness.py,
    │   ├── shadow.py, glitch.py, skulls.py
    └── payloads/               # engine GDI (legado)
        ├── __init__.py         # exporta todos + ALL_PAYLOADS
        ├── base.py             # classe base Payload
        ├── fonts.py            # utilitário de fontes GDI (LOGFONT)
        ├── errors.py, terror.py, eyes.py, angel.py
```

---

## 📜 Licença

Uso educacional.
