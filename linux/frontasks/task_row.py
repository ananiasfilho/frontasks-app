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

"""Uma linha da lista: concluir, editar inline, apagar e arrastar (grip)."""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GObject, GLib, Pango

DND_TARGET = Gtk.TargetEntry.new("FRONTASKS_TASK_ROW", Gtk.TargetFlags.SAME_APP, 0)


class TaskRow(Gtk.ListBoxRow):
    """ListBoxRow que representa uma TaskItem. Emite sinais que o Panel liga
    de volta na TaskStore -- a linha não conhece a store diretamente."""

    __gsignals__ = {
        "toggle": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "title-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "delete": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.set_selectable(False)
        self.set_activatable(False)

        outer = Gtk.EventBox()
        outer.get_style_context().add_class("frontasks-row")
        outer.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.add(outer)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_margin_top(4)
        hbox.set_margin_bottom(4)
        hbox.set_margin_start(6)
        hbox.set_margin_end(6)
        outer.add(hbox)

        # Grip de arraste (reordenar) -- ver README seção 8, dica de reordenar.
        self.grip = Gtk.Label(label="⠿")
        self.grip.get_style_context().add_class("frontasks-grip")
        grip_evbox = Gtk.EventBox()
        grip_evbox.add(self.grip)
        grip_evbox.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK, [DND_TARGET], Gdk.DragAction.MOVE
        )
        grip_evbox.connect("drag-data-get", self._on_drag_data_get)
        hbox.pack_start(grip_evbox, False, False, 0)

        # Checkbox (concluir)
        self.check_btn = Gtk.Button()
        self.check_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.check_label = Gtk.Label(label="○")
        self.check_label.get_style_context().add_class("frontasks-check")
        self.check_btn.add(self.check_label)
        self.check_btn.connect("clicked", lambda *_: self.emit("toggle"))
        hbox.pack_start(self.check_btn, False, False, 0)

        # Título: Label (clique inicia edição) <-> Entry (edita)
        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)

        self.label = Gtk.Label(xalign=0.0)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.get_style_context().add_class("frontasks-title-label")
        label_evbox = Gtk.EventBox()
        label_evbox.add(self.label)
        label_evbox.connect("button-press-event", self._start_edit)

        self.entry = Gtk.Entry()
        self.entry.set_has_frame(False)
        self.entry.get_style_context().add_class("frontasks-title-entry")
        self.entry.connect("activate", self._commit_edit)
        self.entry.connect("focus-out-event", lambda *_: self._commit_edit() or False)
        self.entry.connect("key-press-event", self._on_entry_key)

        self.stack.add_named(label_evbox, "label")
        self.stack.add_named(self.entry, "entry")
        hbox.pack_start(self.stack, True, True, 0)

        # Apagar (só aparece no hover). Fica sempre no layout (reserva espaço)
        # e alterna por opacidade -- show()/hide() depois do layout inicial
        # não recupera alocação de tamanho de forma confiável dentro do
        # ListBox (o botão fica "visível" mas com 1x1px).
        self.delete_btn = Gtk.Button()
        self.delete_btn.set_relief(Gtk.ReliefStyle.NONE)
        delete_label = Gtk.Label(label="✕")
        delete_label.get_style_context().add_class("frontasks-delete")
        self.delete_btn.add(delete_label)
        self.delete_btn.set_opacity(0.0)
        self.delete_btn.set_sensitive(False)
        self.delete_btn.set_tooltip_text("Apagar tarefa")
        self.delete_btn.connect("clicked", lambda *_: self.emit("delete"))
        hbox.pack_start(self.delete_btn, False, False, 0)

        outer.connect("enter-notify-event", self._on_enter)
        outer.connect("leave-notify-event", self._on_leave)
        outer.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        outer.connect("button-press-event", self._on_row_button_press)

        self.show_all()
        self.refresh(task)

    # --- estado visual -------------------------------------------------

    def refresh(self, task):
        self.task = task
        self.label.set_text(task.title)
        self.entry.set_text(task.title)

        ctx = self.check_label.get_style_context()
        ctx2 = self.label.get_style_context()
        if task.isDone:
            ctx.add_class("done")
            ctx2.add_class("done")
            self.check_label.set_text("✔")
            self.label.set_markup(f"<s>{GLib.markup_escape_text(task.title)}</s>")
        else:
            ctx.remove_class("done")
            ctx2.remove_class("done")
            self.check_label.set_text("○")
            self.label.set_text(task.title)

    def _on_enter(self, *_a):
        self.delete_btn.set_opacity(1.0)
        self.delete_btn.set_sensitive(True)

    def _on_leave(self, widget, event):
        # Ignora saída para um filho (ex: indo para o botão apagar).
        alloc = widget.get_allocation()
        if 0 <= event.x < alloc.width and 0 <= event.y < alloc.height:
            return
        self.delete_btn.set_opacity(0.0)
        self.delete_btn.set_sensitive(False)

    # --- edição inline ---------------------------------------------------

    def _start_edit(self, _widget, event=None):
        # Só botão esquerdo inicia edição -- botão direito precisa
        # continuar propagando pro handler de menu de contexto da linha.
        if event is not None and event.button != 1:
            return False
        self.entry.set_text(self.task.title)
        self.stack.set_visible_child_name("entry")
        self.entry.grab_focus()
        self.entry.select_region(0, -1)
        return True

    def _commit_edit(self, *_a):
        new_title = self.entry.get_text().strip()
        self.stack.set_visible_child_name("label")
        if new_title != self.task.title:
            # Título vazio no commit apaga a tarefa (store.update_title trata
            # isso) -- combinado na revisão de UX, não só some silenciosamente.
            self.emit("title-changed", new_title)
        else:
            self.label.set_text(self.task.title)

    def _on_entry_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.entry.set_text(self.task.title)
            self.stack.set_visible_child_name("label")
            return True
        return False

    # --- menu de contexto ------------------------------------------------

    def _on_row_button_press(self, _widget, event):
        if event.button != 3:
            return False
        menu = Gtk.Menu()
        # Guarda referência forte na instância -- um Gtk.Menu só local à
        # função pode ser coletado pelo GC do Python antes do clique no
        # item ser processado (o popup é gerenciado pelo GTK/X11, mas o
        # objeto Python por trás precisa continuar vivo).
        self._context_menu = menu

        toggle_item = Gtk.MenuItem(label="Reabrir" if self.task.isDone else "Concluir")
        toggle_item.connect("activate", lambda *_: self.emit("toggle"))
        menu.append(toggle_item)

        delete_item = Gtk.MenuItem(label="Apagar")
        delete_item.connect("activate", lambda *_: self.emit("delete"))
        menu.append(delete_item)

        menu.attach_to_widget(self, None)
        menu.show_all()
        menu.popup_at_pointer(event)
        return True

    # --- drag reorder -----------------------------------------------------

    def _on_drag_data_get(self, _widget, _context, data, _info, _time):
        data.set(data.get_target(), 8, self.task.id.encode("utf-8"))
