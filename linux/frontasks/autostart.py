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

"""Iniciar no login via .desktop em $XDG_CONFIG_HOME/autostart/ (XDG)."""

import shutil
import sys
from pathlib import Path

from .config import config_dir


def _autostart_dir() -> Path:
    # Mesma base de $XDG_CONFIG_HOME que o resto do app usa (config.py) --
    # antes fixava ~/.config direto, quebrando ambientes com
    # XDG_CONFIG_HOME customizado (achado P2 da revisão técnica).
    return config_dir().parent / "autostart"


def _desktop_file() -> Path:
    return _autostart_dir() / "frontasks.desktop"


DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
Name=FronTasks
Exec={exec_cmd}
Icon=frontasks
X-GNOME-Autostart-enabled=true
"""


def _exec_cmd() -> str:
    """Comando efetivo pra reexecutar o app -- prefere o binário instalado
    no PATH; em execução de dev (fora de instalação via pacote), usa o
    mesmo interpretador Python + `-m frontasks` em vez de assumir
    `frontasks` cegamente (achado P2: comando podia não existir)."""
    found = shutil.which("frontasks")
    if found:
        return found
    return f"{sys.executable} -m frontasks"


def set_enabled(enabled: bool) -> bool:
    """Retorna True se a operação teve sucesso. A UI deve reverter o
    checkbox quando False em vez de assumir que deu certo."""
    try:
        if enabled:
            _autostart_dir().mkdir(parents=True, exist_ok=True)
            _desktop_file().write_text(
                DESKTOP_TEMPLATE.format(exec_cmd=_exec_cmd()), encoding="utf-8"
            )
        else:
            _desktop_file().unlink(missing_ok=True)
        return True
    except OSError:
        return False


def is_enabled() -> bool:
    return _desktop_file().exists()
