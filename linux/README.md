# Frontasks — Guia de Port para Linux (Mint Cinnamon)

> **Para quem é este documento:** é o *briefing* para desenvolver a versão **Linux**
> do Frontasks, do zero, mantendo **paridade de comportamento** e **compatibilidade
> de dados** com a versão macOS já pronta. Escrito para ser lido por um assistente
> de código (outro Claude) rodando **direto no Linux Mint Cinnamon**.

---

## 1. O que é o Frontasks

Um **painel de tarefas flutuante e sempre-no-topo**: fica *sobre* os outros apps,
sempre à vista, sem roubar o foco do que você está fazendo. Leve, redimensionável e
discreto — sem ícone na barra de tarefas, só um ícone na bandeja (tray). Filosofia:
**"formiguinha, não bazuca"** — simples de propósito, para qualquer pessoa usar.

A versão macOS (referência) está em `../macos/` (neste mesmo repositório,
licença **AGPL-3.0**). Use-a como especificação viva.

---

## 2. Paridade de funcionalidades (a meta)

Replicar, com cara nativa de Linux:

- [ ] **Painel flutuante** sempre-no-topo, visível em todos os workspaces
- [ ] **Não rouba o foco** do app de baixo (mas o campo de texto precisa focar ao clicar)
- [ ] **Redimensionável** e **lembra tamanho + posição** entre execuções
- [ ] **1ª vez**: abre no canto superior direito do monitor central
- [ ] **CRUD** de tarefas: criar, editar inline, concluir (checkbox), apagar
- [ ] **Reordenar** arrastando
- [ ] **Limpar concluídas** de uma vez (botão no cabeçalho)
- [ ] **Atalho global** para mostrar/ocultar (equivalente ao ⌥+Espaço do Mac)
- [ ] **Sem entrada na barra de tarefas**; controle por **ícone na bandeja** (mostrar/ocultar, ajustes, sair)
- [ ] **Iniciar no login**
- [ ] **Personalização**: cor de destaque, cor de fundo + transparência, cor do texto (com opção "Automática"), fonte e tamanho
- [ ] **Ícone próprio** (reaproveitar a arte azul de checklist)

---

## 3. Ambiente-alvo

- **Distro:** Linux Mint (base Ubuntu/Debian).
- **Desktop:** Cinnamon → **servidor gráfico X11**, compositor **Muffin** (dá transparência).
- **Implicação boa:** always-on-top, `skip-taskbar` e atalhos globais são triviais no X11.
- **Atenção:** se um dia rodar em **Wayland**, esses três recursos ficam restritos
  (precisam de *portals* e nem sempre funcionam). Manter o alvo em **X11/Cinnamon** por ora.

---

## 4. Stack recomendada: **GTK 3 + Python (PyGObject)**

Por quê:
- O **Cinnamon é feito em GTK** → integração e aparência nativas de graça.
- **Python + PyGObject** é rápido de desenvolver e fácil de iterar (ideal para esse porte).
- Leve, sem runtime pesado (nada de Electron para uma "formiguinha").
- Todos os recursos que precisamos têm binding pronto (GTK, Keybinder, XApp, AppIndicator).

**Alternativas** (se preferir):
- **GTK 4 + Python** — mais moderno, mas GTK 3 é mais estável no Mint e o `keep_above`/
  `skip_taskbar` é mais direto no GTK 3. Recomendo **começar no GTK 3**.
- **Qt (PySide6)** — ótimo e multiplataforma, porém menos "nativo" no Cinnamon.
- **Rust + gtk-rs** ou **Tauri** — performáticos, mas mais esforço; deixe para depois se houver motivo.

---

## 5. Dependências (Mint)

```bash
sudo apt update
sudo apt install \
  python3-gi python3-gi-cairo \
  gir1.2-gtk-3.0 \
  gir1.2-keybinder-3.0 \
  gir1.2-xapp-1.0
# Bandeja alternativa (fallback): gir1.2-appindicator3-0.1
```

- **`gir1.2-gtk-3.0`** — GTK 3.
- **`gir1.2-keybinder-3.0`** — atalho global (grab de tecla no X11).
- **`gir1.2-xapp-1.0`** — `XApp.StatusIcon`, a bandeja **recomendada no Mint/Cinnamon**
  (funciona melhor que `Gtk.StatusIcon` antigo). `AppIndicator3` é fallback cross-DE.

---

## 6. Mapeamento macOS → Linux (X11/GTK3)

| Recurso (Mac) | API macOS | Equivalente Linux (GTK3/X11) |
|---|---|---|
| Painel flutuante | `NSPanel .floating` | `Gtk.Window` + `set_keep_above(True)` |
| Sem barra de título | styleMask sem título | `set_decorated(False)` |
| Sem barra de tarefas | `LSUIElement` | `set_skip_taskbar_hint(True)` + `set_skip_pager_hint(True)` |
| Em todos os Spaces | `.canJoinAllSpaces` | `stick()` |
| Não-ativante | `.nonactivatingPanel` | janela normal keep-above (foco só ao clicar no campo) |
| Redimensionar + lembrar | `setFrameAutosaveName` | resizable nativo; salvar geometria em `configure-event` → arquivo |
| Posição multi-monitor | `NSScreen` | `Gdk.Display`/`Gdk.Monitor` (geometria das telas) |
| Barra de menus / ícone | `MenuBarExtra` | **`XApp.StatusIcon`** (tray) com menu |
| Atalho global | Carbon `RegisterEventHotKey` | **`Keybinder.bind("<Super>space", cb)`** |
| Iniciar no login | `SMAppService` | `.desktop` em `~/.config/autostart/` |
| Fundo translúcido | material + tinta | RGBA visual (`screen.get_rgba_visual()`) + `set_app_paintable(True)` + CSS |
| Tema (cores/fonte) | SwiftUI + `@AppStorage` | **GTK CSS** via `Gtk.CssProvider` + config JSON |
| Persistência | JSON em Application Support | JSON em `~/.config/frontasks/` (XDG) |
| Ícone do app | `.icns` | PNG/SVG no tema `hicolor` + `.desktop` |

**Notas importantes:**
- **Instância única:** o atalho global e o tray devem **alternar a instância existente**,
  não abrir outra. Use `Gio.Application` com `application_id` (single-instance) ou um
  socket em `$XDG_RUNTIME_DIR`.
- **Atalho:** `<Super>space` pode conflitar (algumas configs usam pra troca de layout).
  Bons candidatos: `<Super>t`, `<Ctrl><Alt>t`. Deixe **configurável**. Alternativa nativa:
  o próprio Cinnamon permite "Atalhos personalizados" que rodam um comando — poderia
  chamar `frontasks --toggle`.
- **Transparência** exige compositor ligado (Muffin, padrão no Cinnamon).

---

## 7. Estrutura de projeto sugerida

```
frontasks-linux/
├── frontasks/
│   ├── __main__.py         # entrypoint, Gio.Application single-instance
│   ├── panel.py            # janela flutuante (lista + input)
│   ├── task_row.py         # linha: checkbox, editar inline, apagar
│   ├── store.py            # modelo + persistência JSON
│   ├── settings_window.py  # janela de ajustes
│   ├── tray.py             # XApp.StatusIcon + menu
│   ├── hotkey.py           # Keybinder
│   ├── theming.py          # gera CSS a partir das prefs
│   └── autostart.py        # cria/remove .desktop de autostart
├── data/
│   ├── frontasks.desktop   # lançador
│   └── icons/              # PNG/SVG
├── packaging/              # deb / AppImage / flatpak (fase 2)
├── README.md
└── pyproject.toml          # ou setup.cfg
```

---

## 8. Bootstrap: janela flutuante mínima (prova de conceito)

```python
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class Panel(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_decorated(False)           # sem barra de título
        self.set_keep_above(True)           # SEMPRE no topo
        self.set_skip_taskbar_hint(True)    # fora da barra de tarefas
        self.set_skip_pager_hint(True)
        self.stick()                        # todos os workspaces
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_default_size(300, 420)

        # transparência (Cinnamon tem compositor)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(box)
        # TODO: cabeçalho, lista (Gtk.ListBox), campo "Nova tarefa" (Gtk.Entry)

win = Panel()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
```

Rode com `python3 bootstrap.py` e valide: janela sem bordas, sempre no topo, fora da
barra de tarefas, com transparência. A partir daí, construa a lista e os ajustes.

**Dicas de implementação:**
- **Lista + reordenar:** `Gtk.ListBox` com drag-and-drop (`drag_source_set`/`drag_dest_set`)
  ou reordenação manual via `Gtk.EventBox`. (No GTK4 há `Gtk.ListView` com modelos.)
- **Editar inline:** `Gtk.Entry` sem borda por linha, ou `Gtk.Label` que vira `Entry` no clique.
- **Tema:** monte uma string CSS a partir das prefs e aplique com
  `Gtk.StyleContext.add_provider_for_screen(...)`. A transparência do fundo vem do
  RGBA (`rgba(r,g,b,opacity)` no CSS da janela).

---

## 9. Compatibilidade de dados e configuração

Mantenha o **mesmo formato de dados** da versão Mac para facilitar futura sincronização.

**Tarefas** — `~/.config/frontasks/tasks.json` (lista de objetos):
```json
[
  { "id": "uuid-v4", "title": "Comprar pão e leite", "isDone": false, "createdAt": 774200000, "order": 0 }
]
```
- Campos: `id` (UUID), `title` (string), `isDone` (bool), `createdAt` (número), `order` (int).
- ⚠️ No Mac, `createdAt` é *segundos desde 2001* (data de referência da Foundation). Se
  quiser **portabilidade real** do arquivo entre Mac e Linux, o ideal é **padronizar em
  ISO-8601** nos dois lados (mudança pequena no Mac). Se não for sincronizar agora, use
  epoch Unix no Linux e siga em frente.

**Preferências** — `~/.config/frontasks/settings.json` (espelha as `@AppStorage` do Mac):
```json
{
  "accentHex": "#3B82F6",
  "bgHex": "#2C2C2E",
  "bgOpacity": 0.55,
  "textHex": "auto",
  "fontName": "System",
  "fontSize": 14,
  "launchAtLogin": false
}
```
- `textHex: "auto"` = cor de texto adaptativa (padrão). Qualquer outro valor é hex.
- `fontName: "System"` = fonte padrão do sistema.

Use `XDG_CONFIG_HOME` (padrão `~/.config`). Crie a pasta se não existir.

---

## 10. Iniciar no login (autostart XDG)

Escrever `~/.config/autostart/frontasks.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=Frontasks
Exec=frontasks
Icon=frontasks
X-GNOME-Autostart-enabled=true
```
Ligar/desligar = criar/remover esse arquivo (espelha o toggle "Iniciar no login").

---

## 11. Distribuição no Linux (fase 2 — depois)

| Formato | O que é | Bom pra | Observações |
|---|---|---|---|
| **`.deb`** | Pacote Debian/Ubuntu | **Mint** (nativo) | Instala via `apt`/Software; caminho principal no Mint |
| **AppImage** | Executável único portátil | "Baixou, rodou" | Sem instalar; bom pra releases no GitHub |
| **Flatpak** | Pacote sandboxed universal | Alcance amplo | ⚠️ sandbox **restringe** atalho global/always-on-top (portals) — testar bem |
| **Snap** | Similar ao Flatpak | Ubuntu | Mesmas ressalvas de sandbox |
| **AUR** | Repositório do Arch | Usuários Arch | Não é o público do Mint |

**Recomendação:** comece com **`.deb`** (nativo do Mint) + **AppImage** (portátil no
release do GitHub). Flatpak só depois, validando que o atalho global funciona sob sandbox.

Depois disso, dá pra unificar num só `README`/release multiplataforma e pensar em
Homebrew (Mac) + universal binary — mas isso é assunto da fase seguinte.

---

## 12. Referência: a implementação macOS

O código Swift em `../macos/` é a fonte da verdade do comportamento. Arquivos-chave:

- `Sources/Frontasks/FloatingPanel.swift` — configuração da janela flutuante (o que replicar).
- `Sources/Frontasks/Store.swift` — modelo `TaskItem` + persistência JSON (schema acima).
- `Sources/Frontasks/Views/TaskListView.swift` / `TaskRow.swift` — UI da lista, CRUD, reordenar, limpar.
- `Sources/Frontasks/Views/SettingsView.swift` — ajustes (paletas de cor, fonte, autostart).
- `Sources/Frontasks/HotKeyManager.swift` — atalho global.
- `Sources/Frontasks/PanelController.swift` — posição no monitor central, janela de ajustes.

**Chaves de preferência** e **schema de tarefa** estão nas seções 9 acima — use-os idênticos.

---

## 13. Primeiros passos sugeridos (ordem)

1. Instalar dependências (seção 5) e rodar o **bootstrap** (seção 8).
2. Construir a **lista + input** (CRUD) com persistência JSON (seção 9).
3. **Tema** via CSS (cores/fonte/transparência) lendo `settings.json`.
4. **Bandeja** (`XApp.StatusIcon`) com menu mostrar/ocultar/ajustes/sair.
5. **Atalho global** (Keybinder) + **instância única**.
6. **Reordenar** e **limpar concluídas**.
7. **Persistir geometria** + **posição inicial** no monitor central.
8. **Janela de ajustes** completa + **autostart** (.desktop).
9. **Ícone** e `.desktop` de lançador.
10. Empacotar (**.deb** + **AppImage**).

Boa! Qualquer decisão de arquitetura, prefira o caminho **mais simples e nativo** —
é o espírito do projeto.
