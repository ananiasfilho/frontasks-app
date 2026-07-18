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

"""Ícone na bandeja (XApp.StatusIcon, recomendado no Mint/Cinnamon)."""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")
from gi.repository import Gtk, XApp


class Tray:
    def __init__(self, icon_name: str, on_toggle, on_settings, on_quit):
        self.icon = XApp.StatusIcon()
        self.icon.set_name("FronTasks")
        self.icon.set_tooltip_text("FronTasks — mostrar/ocultar lista")
        self.icon.set_icon_name(icon_name)

        menu = Gtk.Menu()

        item_toggle = Gtk.MenuItem(label="Mostrar / ocultar lista")
        item_toggle.connect("activate", lambda *_: on_toggle())
        menu.append(item_toggle)

        item_settings = Gtk.MenuItem(label="Ajustes…")
        item_settings.connect("activate", lambda *_: on_settings())
        menu.append(item_settings)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Sair do FronTasks")
        item_quit.connect("activate", lambda *_: on_quit())
        menu.append(item_quit)

        menu.show_all()
        # Só o menu secundário (clique direito); clique esquerdo (primário)
        # dispara "activate" -> toggle. Setar primary_menu faria o clique
        # esquerdo abrir o menu em vez de alternar o painel.
        self.icon.set_secondary_menu(menu)
        self.icon.connect("activate", lambda *_a: on_toggle())
