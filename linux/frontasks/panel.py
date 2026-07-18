# FronTasks — floating, always-on-top task list for Linux.
# Copyright (C) 2026 Ananias Filho
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Painel flutuante: cabeçalho, lista de tarefas e barra de nova tarefa.
Equivalente a FloatingPanel.swift + PanelController.swift + TaskListView.swift."""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from .config import geometry_path
from .persistence import atomic_write_json, safe_load_json
from .task_row import TaskRow, DND_TARGET
from . import theming

AUTOSAVE_MARGIN = 32
SAVE_DEBOUNCE_MS = 400


class Panel(Gtk.Window):
    def __init__(self, store, settings, on_settings_clicked):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.store = store
        self.settings = settings
        self.on_settings_clicked = on_settings_clicked

        self._css_provider = Gtk.CssProvider()
        self._css_provider_added = False
        self._save_geometry_source = None
        self._row_widgets = {}

        self.set_title("FronTasks")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.stick()
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_default_size(300, 420)
        self.set_resizable(True)
        self.set_size_request(240, 200)  # mesmo mínimo do Mac (FloatingPanel.swift)
        # Mostrar/alternar o painel (tray, atalho) não deve roubar o foco do
        # app em uso -- só focar de verdade quando o usuário clica no campo
        # de entrada. Ver achado P1 da revisão técnica.
        self.set_focus_on_map(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.get_style_context().add_class("frontasks-panel")

        self._build_ui()
        self.apply_theme()

        self.store.connect("changed", lambda *_: self.refresh_list())
        self.refresh_list()

        self.connect("configure-event", self._on_configure_event)
        self.connect("delete-event", self._on_delete_event)

        if not self._restore_geometry():
            GLib.idle_add(self._position_top_right)

    # --- construção da UI ------------------------------------------------

    def _build_ui(self):
        overlay = Gtk.Overlay()
        self.add(overlay)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        body.get_style_context().add_class("frontasks-body")
        overlay.add(body)
        self.body = body

        self._add_resize_grips(overlay)

        # Cabeçalho. A área de arraste (isMovableByWindowBackground do Mac)
        # cobre só o ícone/título/spacer/contador -- os botões ficam FORA do
        # EventBox de arraste, como filhos diretos do header, pra um clique
        # neles nunca competir com begin_move_drag (achado P1 da revisão).
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.get_style_context().add_class("frontasks-header")
        body.pack_start(header, False, False, 0)

        drag_evbox = Gtk.EventBox()
        drag_evbox.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drag_evbox.connect("button-press-event", self._on_header_button_press)
        header.pack_start(drag_evbox, True, True, 0)

        drag_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        drag_evbox.add(drag_box)

        title_icon = Gtk.Label(label="✓")
        title_icon.get_style_context().add_class("frontasks-accent")
        drag_box.pack_start(title_icon, False, False, 0)

        title = Gtk.Label(label="FronTasks")
        title.get_style_context().add_class("frontasks-title")
        drag_box.pack_start(title, False, False, 0)

        drag_box.pack_start(Gtk.Box(), True, True, 0)  # spacer

        self.pending_label = Gtk.Label()
        self.pending_label.get_style_context().add_class("frontasks-count")
        drag_box.pack_start(self.pending_label, False, False, 0)

        self.clear_btn = Gtk.Button()
        self.clear_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.clear_btn.get_style_context().add_class("frontasks-iconbtn")
        clear_label = Gtk.Label(label="⌫")
        self.clear_btn.add(clear_label)
        self.clear_btn.set_tooltip_text("Limpar concluídas")
        self.clear_btn.connect("clicked", lambda *_: self.store.clear_completed())
        # Sempre no layout; alterna por opacidade (show/hide depois do layout
        # inicial não realoca espaço de forma confiável -- ver task_row.py).
        self.clear_btn.set_opacity(0.0)
        self.clear_btn.set_sensitive(False)
        header.pack_start(self.clear_btn, False, False, 0)

        settings_btn = Gtk.Button()
        settings_btn.set_relief(Gtk.ReliefStyle.NONE)
        settings_btn.get_style_context().add_class("frontasks-iconbtn")
        settings_label = Gtk.Label(label="⚙")
        settings_btn.add(settings_label)
        settings_btn.set_tooltip_text("Ajustes")
        settings_btn.connect("clicked", lambda *_: self.on_settings_clicked())
        header.pack_start(settings_btn, False, False, 0)

        body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Lista / estado vazio
        self.list_stack = Gtk.Stack()
        body.pack_start(self.list_stack, True, True, 0)

        self.empty_label = Gtk.Label(label="Sem tarefas ainda.\nEscreva abaixo para começar.")
        self.empty_label.set_justify(Gtk.Justification.CENTER)
        self.empty_label.get_style_context().add_class("frontasks-empty")
        self.list_stack.add_named(self.empty_label, "empty")

        scroller = Gtk.ScrolledWindow()
        scroller.get_style_context().add_class("frontasks-list")
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("frontasks-list")
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.set_activate_on_single_click(False)
        self.listbox.drag_dest_set(Gtk.DestDefaults.ALL, [DND_TARGET], Gdk.DragAction.MOVE)
        self.listbox.connect("drag-data-received", self._on_drag_data_received)
        scroller.add(self.listbox)
        self.list_stack.add_named(scroller, "list")

        body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Barra de nova tarefa
        input_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        input_bar.get_style_context().add_class("frontasks-input")
        body.pack_start(input_bar, False, False, 0)

        plus_label = Gtk.Label(label="+")
        plus_label.get_style_context().add_class("frontasks-empty")
        input_bar.pack_start(plus_label, False, False, 0)

        self.new_entry = Gtk.Entry()
        self.new_entry.set_placeholder_text("Nova tarefa…")
        self.new_entry.set_has_frame(False)
        self.new_entry.connect("activate", self._on_add_task)
        input_bar.pack_start(self.new_entry, True, True, 0)

    def _add_resize_grips(self, overlay):
        """Tiras invisíveis nas bordas/cantos pra redimensionar arrastando --
        sem decoração (set_decorated(False)) o GTK não dá isso de graça."""
        GRIP = 6
        specs = [
            # (edge, halign, valign, width, height, cursor_name)
            (Gdk.WindowEdge.NORTH, Gtk.Align.FILL, Gtk.Align.START, -1, GRIP, "n-resize"),
            (Gdk.WindowEdge.SOUTH, Gtk.Align.FILL, Gtk.Align.END, -1, GRIP, "s-resize"),
            (Gdk.WindowEdge.WEST, Gtk.Align.START, Gtk.Align.FILL, GRIP, -1, "w-resize"),
            (Gdk.WindowEdge.EAST, Gtk.Align.END, Gtk.Align.FILL, GRIP, -1, "e-resize"),
            (Gdk.WindowEdge.NORTH_WEST, Gtk.Align.START, Gtk.Align.START, GRIP, GRIP, "nw-resize"),
            (Gdk.WindowEdge.NORTH_EAST, Gtk.Align.END, Gtk.Align.START, GRIP, GRIP, "ne-resize"),
            (Gdk.WindowEdge.SOUTH_WEST, Gtk.Align.START, Gtk.Align.END, GRIP, GRIP, "sw-resize"),
            (Gdk.WindowEdge.SOUTH_EAST, Gtk.Align.END, Gtk.Align.END, GRIP, GRIP, "se-resize"),
        ]
        for edge, halign, valign, width, height, cursor_name in specs:
            grip = Gtk.EventBox()
            grip.set_halign(halign)
            grip.set_valign(valign)
            grip.set_size_request(width, height)
            grip.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            grip.connect("button-press-event", self._on_grip_button_press, edge)
            grip.connect("realize", self._on_grip_realize, cursor_name)
            overlay.add_overlay(grip)
            overlay.set_overlay_pass_through(grip, False)

    def _on_grip_realize(self, widget, cursor_name):
        cursor = Gdk.Cursor.new_from_name(self.get_display(), cursor_name)
        if cursor is not None:
            widget.get_window().set_cursor(cursor)

    def _on_grip_button_press(self, _widget, event, edge):
        if event.button == 1:
            self.begin_resize_drag(edge, event.button, int(event.x_root), int(event.y_root), event.time)
        return True

    # --- tema --------------------------------------------------------------

    def apply_theme(self):
        css = theming.build_css(self.settings.data)
        self._css_provider.load_from_data(css.encode("utf-8"))
        # Registrar o mesmo provider mais de uma vez empilha regras
        # redundantes na tela a cada chamada (achado P2) -- só na primeira
        # vez; load_from_data já é suficiente pra atualizar depois.
        if not self._css_provider_added:
            Gtk.StyleContext.add_provider_for_screen(
                self.get_screen(), self._css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            self._css_provider_added = True

    # --- lista ---------------------------------------------------------------

    def refresh_list(self):
        tasks = self.store.tasks
        if not tasks:
            self.list_stack.set_visible_child_name("empty")
        else:
            self.list_stack.set_visible_child_name("list")

        self.pending_label.set_text(
            str(self.store.pending_count) if self.store.pending_count else ""
        )
        has_done = self.store.done_count > 0
        self.clear_btn.set_opacity(1.0 if has_done else 0.0)
        self.clear_btn.set_sensitive(has_done)

        existing_ids = {t.id for t in tasks}
        for task_id in list(self._row_widgets):
            if task_id not in existing_ids:
                del self._row_widgets[task_id]

        for row in list(self.listbox.get_children()):
            self.listbox.remove(row)

        for task in tasks:
            row = self._row_widgets.get(task.id)
            if row is None:
                row = TaskRow(task)
                row.connect("toggle", lambda r: self.store.toggle(r.task.id))
                row.connect(
                    "title-changed", lambda r, title: self.store.update_title(r.task.id, title)
                )
                row.connect("delete", lambda r: self.store.delete(r.task.id))
                self._row_widgets[task.id] = row
            else:
                row.refresh(task)
            self.listbox.add(row)

    def _on_drag_data_received(self, _widget, context, x, y, data, _info, time):
        raw = data.get_data()
        if not raw:
            Gtk.drag_finish(context, False, False, time)
            return
        task_id = raw.decode("utf-8")
        old_index = next(
            (i for i, t in enumerate(self.store.tasks) if t.id == task_id), None
        )
        if old_index is None:
            Gtk.drag_finish(context, False, False, time)
            return

        target_row = self.listbox.get_row_at_y(y)
        if target_row is None:
            new_index = len(self.store.tasks) - 1
        else:
            target_index = target_row.get_index()
            alloc = target_row.get_allocation()
            # Soltar na metade de baixo da linha insere DEPOIS dela, não antes.
            if y > alloc.y + alloc.height / 2:
                target_index += 1
            # Remover a linha de origem desloca os índices depois dela.
            if target_index > old_index:
                target_index -= 1
            new_index = max(0, min(target_index, len(self.store.tasks) - 1))

        ok = self.store.move(old_index, new_index)
        Gtk.drag_finish(context, ok, False, time)

    def _on_add_task(self, *_a):
        title = self.new_entry.get_text()
        self.store.add(title)
        self.new_entry.set_text("")
        self.new_entry.grab_focus()

    def _on_header_button_press(self, _widget, event):
        if event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
        return False

    # --- geometria (posição + tamanho) ------------------------------------------

    def _on_configure_event(self, *_a):
        if self._save_geometry_source is not None:
            GLib.source_remove(self._save_geometry_source)
        self._save_geometry_source = GLib.timeout_add(SAVE_DEBOUNCE_MS, self._save_geometry)
        return False

    def _save_geometry(self):
        self._save_geometry_source = None
        x, y = self.get_position()
        w, h = self.get_size()
        atomic_write_json(geometry_path(), {"x": x, "y": y, "width": w, "height": h})
        return False

    @staticmethod
    def _validate_geometry(raw):
        if not isinstance(raw, dict):
            raise ValueError("geometry.json: esperava um objeto")
        x, y = int(raw["x"]), int(raw["y"])
        w, h = int(raw["width"]), int(raw["height"])
        if w < 240 or h < 200:
            raise ValueError("geometry.json: tamanho menor que o mínimo")
        return {"x": x, "y": y, "width": w, "height": h}

    def _restore_geometry(self) -> bool:
        g = safe_load_json(geometry_path(), validate=self._validate_geometry)
        if g is None:
            return False

        # Se o monitor/layout mudou desde a última execução (monitor removido,
        # resolução diferente), a posição salva pode cair fora de qualquer
        # tela -- confere interseção com o workarea atual antes de aplicar
        # (achado P2 da revisão técnica).
        display = Gdk.Display.get_default()
        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = g["x"], g["y"], g["width"], g["height"]
        visible = False
        for i in range(display.get_n_monitors()):
            workarea = display.get_monitor(i).get_workarea()
            intersects, _ = workarea.intersect(rect)
            if intersects:
                visible = True
                break
        if not visible:
            return False

        self.resize(g["width"], g["height"])
        self.move(g["x"], g["y"])
        return True

    def _position_top_right(self):
        """Abre no canto superior direito do monitor 'central' (que contém o
        centro da união de todas as telas) -- ver PanelController.swift."""
        display = Gdk.Display.get_default()
        n = display.get_n_monitors()
        if n == 0:
            return False

        geoms = [display.get_monitor(i).get_geometry() for i in range(n)]
        union_x0 = min(g.x for g in geoms)
        union_y0 = min(g.y for g in geoms)
        union_x1 = max(g.x + g.width for g in geoms)
        union_y1 = max(g.y + g.height for g in geoms)
        cx = (union_x0 + union_x1) / 2
        cy = (union_y0 + union_y1) / 2

        central = display.get_monitor(0)
        for i, g in enumerate(geoms):
            if g.x <= cx < g.x + g.width and g.y <= cy < g.y + g.height:
                central = display.get_monitor(i)
                break

        workarea = central.get_workarea()
        w, h = self.get_size()
        x = workarea.x + workarea.width - w - AUTOSAVE_MARGIN
        y = workarea.y + AUTOSAVE_MARGIN
        self.move(x, y)
        return False

    def _on_delete_event(self, *_a):
        # Sem botão de fechar (decorated=False); qualquer delete-event vira
        # apenas "ocultar", igual ao hidesOnDeactivate=false do Mac.
        self.hide()
        return True
