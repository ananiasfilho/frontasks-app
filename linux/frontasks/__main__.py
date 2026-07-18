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

"""Entrypoint. Gtk.Application garante instância única (mesmo application_id):
uma segunda invocação de `frontasks` dispara 'activate' na instância existente
em vez de abrir outro processo -- ver README seção 6, nota "Instância única"."""

import shutil
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from .store import TaskStore
from .settings import Settings
from .panel import Panel
from .settings_window import SettingsWindow
from .tray import Tray
from .hotkey import HotkeyManager

APP_ID = "org.frontasks.FronTasks"
ICONS_DIR = str(Path(__file__).parent / "data" / "icons")
SOURCE_ICON = Path(__file__).parent / "data" / "icons" / "frontasks.png"


def _is_installed_via_package() -> bool:
    """True quando rodando a partir de um .deb/.rpm instalado (o pacote já
    põe o ícone em /usr/share/icons/hicolor/ -- ver packaging/). False só
    em execução "de dev", direto do checkout do repositório."""
    return str(Path(__file__).resolve()).startswith("/usr/")


def _install_icon():
    """Copia o ícone para ~/.local/share/icons/hicolor/ (tema padrão XDG) --
    só em execução de dev. Instalado via pacote, isso deixaria resíduo fora
    do gerenciador de pacotes após uma desinstalação (achado da revisão
    técnica).

    Necessário em dev porque o ícone da bandeja é resolvido por um processo
    separado (xapp-sn-watcher/StatusNotifier host), que não enxerga o
    search-path do Gtk.IconTheme do nosso próprio processo -- só encontra
    ícones já instalados num tema de ícones padrão."""
    if _is_installed_via_package():
        return
    dest_dir = Path.home() / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    dest = dest_dir / "frontasks.png"
    if dest.exists() and dest.stat().st_mtime >= SOURCE_ICON.stat().st_mtime:
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_ICON, dest)


class FronTasksApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.store = None
        self.settings = None
        self.panel = None
        self.settings_window = None
        self.tray = None
        self.hotkey = None
        self._started = False

    def do_startup(self):
        Gtk.Application.do_startup(self)
        _install_icon()
        Gtk.IconTheme.get_default().append_search_path(ICONS_DIR)
        Gtk.Window.set_default_icon_name("frontasks")

    def do_activate(self):
        if self._started:
            self.toggle_panel()
            return
        self._started = True

        self.store = TaskStore()
        self.settings = Settings()

        self.panel = Panel(self.store, self.settings, self.show_settings)
        self.add_window(self.panel)
        self.panel.show_all()
        # Gtk.Stack ignora set_visible_child_name() chamado antes do primeiro
        # show_all() (volta pro primeiro filho) -- resincroniza agora.
        self.panel.refresh_list()

        self.tray = Tray(
            icon_name="frontasks",
            on_toggle=self.toggle_panel,
            on_settings=self.show_settings,
            on_quit=self.quit,
        )

        self.hotkey = HotkeyManager(self.settings.get("hotkey"), self.toggle_panel)
        if not self.hotkey.bind():
            print(
                f"FronTasks: não consegui registrar o atalho global "
                f"'{self.hotkey.accel}' (em uso por outro app, ou sem suporte "
                f"no ambiente atual -- ex.: Wayland). Use a bandeja."
            )

    def toggle_panel(self):
        if self.panel.get_visible():
            self.panel.hide()
        else:
            # show() (não present()): alternar pelo atalho/bandeja não deve
            # roubar o foco do app em uso -- ver achado P1 da revisão.
            self.panel.show()

    def show_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow(
                self.settings, self.panel.apply_theme, self.hotkey
            )
            self.settings_window.connect("destroy", self._on_settings_closed)
        self.settings_window.present()

    def _on_settings_closed(self, *_a):
        self.settings_window = None


def main():
    app = FronTasksApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
