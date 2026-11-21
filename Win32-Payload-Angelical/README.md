# Win32-Payload-Angelical 👁️‍🗨️🔥

> Motor de efeitos visuais **GDI** para Windows, com tema de **horror / terror angelical**.
> Projeto educacional em Python inspirado no [`Win32-Payload-Engine`](https://github.com/panda12332145/Win32-Payload-Engine).

Desenha diretamente sobre a área de trabalho do Windows usando **apenas** a API GDI
(`win32gui`, `win32con`, `win32api` do pacote **pywin32**) — sem PIL, pygame, tkinter
ou qualquer outra dependência de interface.

O destaque do projeto é o **Anjo Trono (Ophanim)**: uma recriação animada do anjo bíblico
descrito em Ezequiel (rodas dentro de rodas, cobertas de olhos), desenhado inteiramente
com primitivas GDI e com animação quadro a quadro.

---

## ⚠️ Aviso importante

- Este projeto é **educacional**, voltado ao aprendizado de **computação gráfica com GDI**
  (rotação 3D, projeção em perspectiva, polígonos, animação frame-a-frame).
- Os efeitos são **puramente visuais** e **temporários**: eles desenham sobre a tela, mas
  **não** modificam arquivos, não persistem após o fechamento, não exploram falhas, não
  evadem antivírus e não possuem qualquer capacidade ofensiva. Pressione **ESC** ou
  **Ctrl+C** para encerrar; a tela se recompõe normalmente.
- Funciona **somente no Windows** (depende da GDI via pywin32).

---

## 📦 Instalação

```bash
# No Windows, com Python 3.8+
git clone https://github.com/panda12332145/Win32-Payload-Angelical.git
cd Win32-Payload-Angelical
pip install -r requirements.txt
```

## ▶️ Como usar

```bash
python main.py            # abre o menu interativo
python main.py --list     # lista todos os payloads
python main.py --angel    # abre direto o Anjo Trono (Ophanim)
python main.py --all      # roda todos os efeitos em sequência
python main.py --fps 60   # define o FPS (padrão: 30)
```

Durante a execução, pressione **ESC** (ou **Ctrl+C**) para encerrar o efeito atual.

---

## 🎭 Payloads disponíveis

### 💥 Erros
| Payload | Efeito |
|---|---|
| `BlueScreenPayload` | Tela Azul da Morte (BSOD) falsa com *stop code*. |
| `ErrorDialogPayload` | Enxame de caixas de diálogo de erro falsas. |
| `GlitchPayload` | Blocos RGB aleatórios (corrupção de vídeo / glitch). |

### 🩸 Terror
| Payload | Efeito |
|---|---|
| `BloodDropPayload` | Gotas de sangue caindo com gravidade e acúmulo no fundo. |
| `CracksPayload` | Rachaduras negras se espalhando e bifurcando pela tela. |
| `ShadowFigurePayload` | Silhueta humanoide sombria surgindo e sumindo em *fade*. |
| `SkullPayload` | Crânios desenhados em GDI (órbitas, dentes, mandíbula). |
| `DarknessPayload` | Vinheta de escuridão pulsante com estrelas distantes. |

### 👁️ Olhos
| Payload | Efeito |
|---|---|
| `EyesPayload` | 15–25 olhos observando, piscando de forma independente, íris dourada/vermelha, pupilas que acompanham o centro da tela e veias vermelhas. |

### 😇 Anjo principal
| Payload | Efeito |
|---|---|
| `OphanimAngelPayload` | **Anjo Trono bíblico completo e animado.** |

---

## 😇 O Anjo Trono (Ophanim)

Recriação do anjo bíblico (Ezequiel 1 e 10), **100% desenhado e animado em GDI**:

- **3 anéis concêntricos** girando em **velocidades e direções diferentes**, usando
  **rotação 3D + projeção em perspectiva** (mesma técnica do `IconCubePayload` original).
- Cada anel é **coberto de olhos** distribuídos pela circunferência.
- **Olho central gigante** com íris dourada, pupila vermelho-sangue e **piscar dramático**.
- **Duas asas simétricas** com penas em `Polygon`, **batendo** em onda senoidal.
- **Partículas de fogo** subindo ao fundo.
- **Brilho / chama pulsante** (elipses concêntricas em cores quentes).
- **Texto sagrado flutuante**: *"KADOSH KADOSH KADOSH"* / *"SANTO SANTO SANTO"*.

**Paleta:** dourado `RGB(255,215,0)`, vermelho vivo `RGB(220,20,60)`,
vermelho-sangue `RGB(139,0,0)`, laranja-fogo `RGB(255,69,0)`, branco e preto.

### Estado da animação (por quadro)
- `ring_angles[3]` — ângulos dos 3 anéis (incrementados por frame).
- `ring_tilts[3]` — inclinação 3D oscilante de cada anel.
- `eye_blink` — ciclo de piscar do olho central.
- `wing_phase` — fase de batimento das asas (seno).
- `fire_particles` — lista de partículas de fogo.
- `glow_pulse` — pulso senoidal do brilho.

---

## 🧱 Estrutura do projeto

```
Win32-Payload-Angelical/
├── main.py                 # menu interativo / CLI
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── src/
    ├── __init__.py
    ├── engine.py           # loop de animação (FPS, ESC, stateful/stateless)
    └── payloads/
        ├── __init__.py     # exporta todos + ALL_PAYLOADS
        ├── base.py         # classe base Payload
        ├── errors.py       # BSOD, diálogos de erro, glitch
        ├── terror.py       # sangue, rachaduras, sombra, crânios, escuridão
        ├── eyes.py         # olhos vigilantes
        └── angel.py        # Anjo Trono (Ophanim) animado
```

---

## 🧠 Como funciona o engine

O motor obtém o *Device Context* da área de trabalho e chama `draw(hdc, w, h)` em loop:

```python
hwnd = win32gui.GetDesktopWindow()
hdc  = win32gui.GetDC(hwnd)
payload.draw(hdc, w, h)
win32gui.ReleaseDC(hwnd, hdc)
```

- **Payloads com estado** (`stateful = True`) mantêm a mesma instância entre quadros,
  permitindo animação fluida (anéis girando, asas batendo, olhos piscando).
- **Payloads sem estado** redesenham um quadro completo a cada chamada.
- FPS configurável via `time.sleep(1/fps)`; **ESC** encerra via `GetAsyncKeyState`.

---

## 📜 Licença

Uso educacional. Veja o repositório original para referência de técnicas GDI.
