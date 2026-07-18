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

"""Preferências, persistidas em settings.json (espelha os @AppStorage do Mac)."""

from . import theming
from .config import settings_path
from .persistence import atomic_write_json, safe_load_json

DEFAULTS = {
    "accentHex": "#3B82F6",
    "bgHex": "#2C2C2E",
    "bgOpacity": 0.55,
    "textHex": "auto",
    "fontName": "System",
    "fontSize": 14,
    "launchAtLogin": False,
    # Atalho global. Sem UI de edição (o Mac também só exibe, não edita) --
    # troque aqui ou direto em settings.json se conflitar no seu Cinnamon.
    # <Ctrl><Alt>t evitado de propósito: é o atalho padrão de "abrir
    # terminal" em Cinnamon/GNOME/Ubuntu (achado da revisão técnica).
    "hotkey": "<Ctrl><Super>t",
}

# (validador, valor-default de fallback quando o tipo/valor não bate)
_VALIDATORS = {
    "accentHex": (lambda v: isinstance(v, str), DEFAULTS["accentHex"]),
    "bgHex": (lambda v: isinstance(v, str), DEFAULTS["bgHex"]),
    "bgOpacity": (lambda v: isinstance(v, (int, float)) and 0.0 <= v <= 1.0, DEFAULTS["bgOpacity"]),
    "textHex": (lambda v: isinstance(v, str), DEFAULTS["textHex"]),
    "fontName": (lambda v: isinstance(v, str), DEFAULTS["fontName"]),
    "fontSize": (lambda v: isinstance(v, (int, float)) and 6 <= v <= 72, DEFAULTS["fontSize"]),
    "launchAtLogin": (lambda v: isinstance(v, bool), DEFAULTS["launchAtLogin"]),
    "hotkey": (lambda v: isinstance(v, str) and bool(v), DEFAULTS["hotkey"]),
}


def _validate_settings(raw) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("settings.json: esperava um objeto")
    clean = {}
    for key, (is_valid, fallback) in _VALIDATORS.items():
        if key in raw:
            try:
                ok = is_valid(raw[key])
            except Exception:
                ok = False
            clean[key] = raw[key] if ok else fallback
    return clean


class Settings:
    def __init__(self):
        self._path = settings_path()
        self.data = dict(DEFAULTS)
        if not self._path.exists():
            # Primeira execução (sem settings.json ainda): usa a cor de
            # fundo do tema GTK/Cinnamon ativo em vez do grafite fixo
            # herdado do Mac.
            self.data["bgHex"] = theming.detect_theme_bg_hex(DEFAULTS["bgHex"])
        self.load()

    def load(self):
        loaded = safe_load_json(self._path, validate=_validate_settings)
        if loaded is not None:
            self.data.update(loaded)

    def save(self):
        atomic_write_json(self._path, self.data)

    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()
