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

"""Paletas de cor (mesmas do Mac Support.swift) e geração de CSS GTK a partir
das preferências."""

import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

TEXT_PRESETS = [
    ("Automática", "auto"),
    ("Branco", "#FFFFFF"),
    ("Cinza claro", "#C7CBD1"),
    ("Preto", "#111111"),
    ("Azul", "#3B82F6"),
    ("Verde", "#22C55E"),
    ("Amarelo", "#EAB308"),
    ("Vermelho", "#EF4444"),
]

BACKGROUND_PRESETS = [
    ("Grafite", "#2C2C2E"),
    ("Cinza", "#48484A"),
    ("Azul-noite", "#1E293B"),
    ("Verde-musgo", "#14342B"),
    ("Vinho", "#3B1D2B"),
    ("Roxo escuro", "#241B36"),
    ("Areia", "#EAE0D5"),
    ("Branco", "#FFFFFF"),
]

ACCENT_PRESETS = [
    ("Azul", "#3B82F6"),
    ("Índigo", "#6366F1"),
    ("Roxo", "#8B5CF6"),
    ("Rosa", "#EC4899"),
    ("Vermelho", "#EF4444"),
    ("Laranja", "#F97316"),
    ("Amarelo", "#EAB308"),
    ("Verde", "#22C55E"),
    ("Turquesa", "#14B8A6"),
    ("Grafite", "#6B7280"),
]

_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}$")


def safe_hex(value: str, default: str = "#3B82F6") -> str:
    if isinstance(value, str) and _HEX_RE.match(value):
        return value
    return default


def _rgba_to_hex(rgba) -> str:
    return "#%02X%02X%02X" % (
        round(rgba.red * 255), round(rgba.green * 255), round(rgba.blue * 255)
    )


def detect_theme_bg_hex(fallback: str = "#2C2C2E") -> str:
    """Cor de fundo do tema GTK/Cinnamon ativo no momento -- usada só como
    semente do `bgHex` na primeira execução (antes de existir settings.json).
    Depois disso o usuário controla tudo pelos Ajustes."""
    try:
        win = Gtk.OffscreenWindow()
        box = Gtk.Box()
        win.add(box)
        win.show_all()
        ctx = box.get_style_context()
        found, rgba = ctx.lookup_color("theme_bg_color")
        if not found:
            rgba = ctx.get_background_color(Gtk.StateFlags.NORMAL)
        hex_value = _rgba_to_hex(rgba)
        win.destroy()
        return hex_value
    except Exception:
        return fallback


def build_css(prefs: dict) -> str:
    accent = safe_hex(prefs.get("accentHex", "#3B82F6"))
    bg = safe_hex(prefs.get("bgHex", "#2C2C2E"))
    bg_opacity = max(0.1, min(1.0, float(prefs.get("bgOpacity", 0.55))))
    text_hex = prefs.get("textHex", "auto")
    font_name = prefs.get("fontName", "System")
    font_size = round(float(prefs.get("fontSize", 14)))

    font_family_css = "" if font_name == "System" else f'font-family: "{font_name}";'
    if text_hex == "auto":
        text_css = ""
        text_done_css = "opacity: 0.45;"
    else:
        text_hex = safe_hex(text_hex, "#FFFFFF")
        text_css = f"color: {text_hex};"
        text_done_css = f"color: alpha({text_hex}, 0.45);"

    return f"""
    window.frontasks-panel {{
        background-color: transparent;
    }}

    .frontasks-body {{
        background-color: alpha({bg}, {bg_opacity});
        border-radius: 12px;
        border: 1px solid alpha(#ffffff, 0.10);
    }}

    .frontasks-body button {{
        background: transparent;
        background-image: none;
        border: none;
        box-shadow: none;
        outline: none;
        padding: 2px;
        min-width: 0;
        min-height: 0;
    }}
    .frontasks-body button:hover, .frontasks-body button:focus {{
        background-color: alpha(#ffffff, 0.08);
        border-radius: 6px;
    }}

    .frontasks-header {{
        padding: 6px 10px;
    }}

    .frontasks-title {{
        font-weight: 600;
    }}

    .frontasks-accent {{
        color: {accent};
    }}

    .frontasks-count {{
        opacity: 0.6;
        font-size: 0.9em;
    }}

    .frontasks-iconbtn {{
        opacity: 0.6;
        padding: 2px;
    }}
    .frontasks-iconbtn:hover {{
        opacity: 1;
    }}

    .frontasks-empty {{
        opacity: 0.55;
    }}

    scrolledwindow.frontasks-list, scrolledwindow.frontasks-list viewport {{
        background-color: transparent;
    }}
    list.frontasks-list {{
        background-color: transparent;
    }}
    list.frontasks-list row {{
        background-color: transparent;
        padding: 0;
    }}

    .frontasks-row {{
        border-radius: 6px;
    }}
    .frontasks-row:hover {{
        background-color: alpha(#ffffff, 0.07);
    }}

    .frontasks-grip {{
        opacity: 0.35;
    }}

    .frontasks-check {{
        opacity: 0.55;
        font-size: 1.15em;
        {text_css}
    }}
    .frontasks-check.done {{
        opacity: 1;
        color: {accent};
    }}

    .frontasks-delete {{
        opacity: 0.7;
        color: #EF4444;
    }}

    .frontasks-title-label, .frontasks-title-entry {{
        {font_family_css}
        font-size: {font_size}px;
        {text_css}
    }}
    .frontasks-title-label.done {{
        {text_done_css}
    }}

    .frontasks-title-entry {{
        background: transparent;
        border: none;
        box-shadow: none;
        padding: 2px 0;
    }}

    .frontasks-input {{
        padding: 6px 10px;
    }}
    .frontasks-input entry {{
        background: transparent;
        border: none;
        box-shadow: none;
        {font_family_css}
        font-size: {font_size}px;
        {text_css}
    }}
    """
