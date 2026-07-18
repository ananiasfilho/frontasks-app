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

"""Janela de Ajustes: cores (fundo/destaque/texto), fonte e sistema.
Equivalente a SettingsView.swift."""

import math

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib, Pango, PangoCairo

from . import theming
from . import autostart

SWATCH_SIZE = 26


def _hex_to_rgb(hex_color: str):
    hex_color = theming.safe_hex(hex_color, "#3B82F6").lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


class ColorSwatch(Gtk.Button):
    """Círculo de cor clicável, com anel quando selecionado. "auto" desenha
    meio branco / meio preto (cor de texto adaptativa)."""

    def __init__(self, hex_value: str, size: int = SWATCH_SIZE):
        super().__init__()
        self.hex_value = hex_value
        self.selected = False
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_size_request(size + 6, size + 6)
        self.da = Gtk.DrawingArea()
        self.da.set_size_request(size, size)
        self.da.connect("draw", self._on_draw)
        self.add(self.da)

    def set_selected(self, value: bool):
        self.selected = value
        self.da.queue_draw()

    def _on_draw(self, widget, cr):
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        cx, cy, r = w / 2, h / 2, min(w, h) / 2 - 2

        if self.hex_value == "auto":
            cr.save()
            cr.arc(cx, cy, r, 0, 2 * math.pi)
            cr.clip()
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(cx - r, cy - r, r, 2 * r)
            cr.fill()
            cr.set_source_rgb(0.05, 0.05, 0.05)
            cr.rectangle(cx, cy - r, r, 2 * r)
            cr.fill()
            cr.restore()
        else:
            rr, gg, bb = _hex_to_rgb(self.hex_value)
            cr.set_source_rgb(rr, gg, bb)
            cr.arc(cx, cy, r, 0, 2 * math.pi)
            cr.fill()

        cr.set_source_rgba(0, 0, 0, 0.18)
        cr.set_line_width(1)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()

        if self.selected:
            cr.set_source_rgba(0.2, 0.5, 1.0, 0.9)
            cr.set_line_width(2)
            cr.arc(cx, cy, r + 2, 0, 2 * math.pi)
            cr.stroke()
        return False


def _swatch_row(presets, current_getter, on_pick):
    flow = Gtk.FlowBox()
    flow.set_selection_mode(Gtk.SelectionMode.NONE)
    flow.set_max_children_per_line(10)
    flow.set_min_children_per_line(4)
    flow.set_row_spacing(6)
    flow.set_column_spacing(6)

    swatches = []

    def refresh_selection():
        current = current_getter()
        for sw in swatches:
            sw.set_selected(sw.hex_value.lower() == str(current).lower())

    for name, hex_value in presets:
        sw = ColorSwatch(hex_value)
        sw.set_tooltip_text(name)
        sw.connect("clicked", lambda _b, hv=hex_value: (on_pick(hv), refresh_selection()))
        swatches.append(sw)
        flow.add(sw)

    refresh_selection()
    return flow, refresh_selection


class SettingsWindow(Gtk.Window):
    def __init__(self, settings, on_theme_changed, hotkey=None):
        super().__init__(title="Ajustes do FronTasks")
        self.settings = settings
        self.on_theme_changed = on_theme_changed
        self.hotkey = hotkey
        self._apply_debounce_source = None

        self.set_default_size(400, 640)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.connect("delete-event", self._on_close)

        scroller = Gtk.ScrolledWindow()
        self.add(scroller)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.set_margin_top(14)
        root.set_margin_bottom(14)
        root.set_margin_start(14)
        root.set_margin_end(14)
        scroller.add(root)

        root.pack_start(self._build_background_section(), False, False, 0)
        root.pack_start(self._build_accent_section(), False, False, 0)
        root.pack_start(self._build_text_section(), False, False, 0)
        root.pack_start(self._build_font_section(), False, False, 0)
        root.pack_start(self._build_system_section(), False, False, 0)

        self.show_all()

    # --- helpers ------------------------------------------------------------

    def _apply(self):
        # settings.set() já salva -- não salvar de novo aqui (achado P2 da
        # revisão: cada evento de slider regravava o arquivo duas vezes).
        self.on_theme_changed()

    def _apply_debounced(self, delay_ms=120):
        """Pra sliders (opacidade/tamanho de fonte): o valor já foi salvo em
        settings.set(), mas reaplicar o CSS a cada pixel de arraste é
        desperdício -- adia e faz só uma vez que o arraste pausar."""
        if self._apply_debounce_source is not None:
            GLib.source_remove(self._apply_debounce_source)

        def _fire():
            self._apply_debounce_source = None
            self.on_theme_changed()
            return False

        self._apply_debounce_source = GLib.timeout_add(delay_ms, _fire)

    def _section(self, title):
        frame = Gtk.Frame(label=title)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.add(box)
        return frame, box

    # --- seções ------------------------------------------------------------

    def _build_background_section(self):
        frame, box = self._section("Fundo do cartão")

        flow, refresh = _swatch_row(
            theming.BACKGROUND_PRESETS,
            lambda: self.settings.get("bgHex"),
            lambda hv: (self.settings.set("bgHex", hv), self._apply()),
        )
        box.pack_start(flow, False, False, 0)

        custom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        custom_row.pack_start(Gtk.Label(label="Personalizada…"), False, False, 0)
        color_btn = Gtk.ColorButton()
        color_btn.set_use_alpha(False)
        rgba = Gdk.RGBA()
        rgba.parse(theming.safe_hex(self.settings.get("bgHex")))
        color_btn.set_rgba(rgba)

        def on_custom(btn):
            c = btn.get_rgba()
            hexv = "#%02X%02X%02X" % (round(c.red * 255), round(c.green * 255), round(c.blue * 255))
            self.settings.set("bgHex", hexv)
            self._apply()
            refresh()

        color_btn.connect("color-set", on_custom)
        custom_row.pack_start(color_btn, False, False, 0)
        box.pack_start(custom_row, False, False, 0)

        opacity_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        opacity_row.pack_start(Gtk.Label(label="Transparência"), False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.1, 1.0, 0.01)
        scale.set_value(float(self.settings.get("bgOpacity")))
        scale.set_hexpand(True)
        scale.set_draw_value(False)
        pct_label = Gtk.Label(label=f"{round(float(self.settings.get('bgOpacity')) * 100)}%")

        def on_opacity(sc):
            v = sc.get_value()
            self.settings.set("bgOpacity", v)
            pct_label.set_text(f"{round(v * 100)}%")
            self._apply_debounced()

        scale.connect("value-changed", on_opacity)
        opacity_row.pack_start(scale, True, True, 0)
        opacity_row.pack_start(pct_label, False, False, 0)
        box.pack_start(opacity_row, False, False, 0)

        return frame

    def _build_accent_section(self):
        frame, box = self._section("Cor de destaque")
        flow, refresh = _swatch_row(
            theming.ACCENT_PRESETS,
            lambda: self.settings.get("accentHex"),
            lambda hv: (self.settings.set("accentHex", hv), self._apply()),
        )
        box.pack_start(flow, False, False, 0)

        custom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        custom_row.pack_start(Gtk.Label(label="Personalizada…"), False, False, 0)
        color_btn = Gtk.ColorButton()
        color_btn.set_use_alpha(False)
        rgba = Gdk.RGBA()
        rgba.parse(theming.safe_hex(self.settings.get("accentHex")))
        color_btn.set_rgba(rgba)

        def on_custom(btn):
            c = btn.get_rgba()
            hexv = "#%02X%02X%02X" % (round(c.red * 255), round(c.green * 255), round(c.blue * 255))
            self.settings.set("accentHex", hexv)
            self._apply()
            refresh()

        color_btn.connect("color-set", on_custom)
        custom_row.pack_start(color_btn, False, False, 0)
        box.pack_start(custom_row, False, False, 0)
        return frame

    def _build_text_section(self):
        frame, box = self._section("Cor do texto")
        flow, refresh = _swatch_row(
            theming.TEXT_PRESETS,
            lambda: self.settings.get("textHex"),
            lambda hv: (self.settings.set("textHex", hv), self._apply()),
        )
        box.pack_start(flow, False, False, 0)

        custom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        custom_row.pack_start(Gtk.Label(label="Personalizada…"), False, False, 0)
        color_btn = Gtk.ColorButton()
        color_btn.set_use_alpha(False)
        current_text = self.settings.get("textHex")
        rgba = Gdk.RGBA()
        rgba.parse(current_text if current_text != "auto" else "#FFFFFF")
        color_btn.set_rgba(rgba)

        def on_custom(btn):
            c = btn.get_rgba()
            hexv = "#%02X%02X%02X" % (round(c.red * 255), round(c.green * 255), round(c.blue * 255))
            self.settings.set("textHex", hexv)
            self._apply()
            refresh()

        color_btn.connect("color-set", on_custom)
        custom_row.pack_start(color_btn, False, False, 0)
        box.pack_start(custom_row, False, False, 0)
        return frame

    def _build_font_section(self):
        frame, box = self._section("Fonte")

        families = ["System"] + sorted(
            {f.get_name() for f in PangoCairo.FontMap.get_default().list_families()}
        )
        combo = Gtk.ComboBoxText()
        for fam in families:
            combo.append_text(fam)
        current_font = self.settings.get("fontName")
        combo.set_active(families.index(current_font) if current_font in families else 0)

        def on_font(cb):
            self.settings.set("fontName", cb.get_active_text())
            self._apply()

        combo.connect("changed", on_font)
        box.pack_start(combo, False, False, 0)

        size_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        size_row.pack_start(Gtk.Label(label="Tamanho"), False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 10, 28, 1)
        scale.set_value(round(float(self.settings.get("fontSize"))))
        scale.set_hexpand(True)
        scale.set_draw_value(False)
        scale.set_round_digits(0)
        size_label = Gtk.Label(label=f"{int(self.settings.get('fontSize'))} pt")

        def on_size(sc):
            v = round(sc.get_value())
            self.settings.set("fontSize", v)
            size_label.set_text(f"{v} pt")
            self._apply_debounced()

        scale.connect("value-changed", on_size)
        size_row.pack_start(scale, True, True, 0)
        size_row.pack_start(size_label, False, False, 0)
        box.pack_start(size_row, False, False, 0)

        return frame

    def _build_system_section(self):
        frame, box = self._section("Sistema")

        check = Gtk.CheckButton(label="Iniciar ao ligar o computador")
        check.set_active(autostart.is_enabled())

        def on_toggle(btn):
            enabled = btn.get_active()
            if autostart.set_enabled(enabled):
                self.settings.set("launchAtLogin", enabled)
            else:
                # Falhou (permissão, disco, etc.) -- reverte o checkbox em
                # vez de fingir que funcionou (achado P2 da revisão).
                btn.handler_block_by_func(on_toggle)
                btn.set_active(not enabled)
                btn.handler_unblock_by_func(on_toggle)

        check.connect("toggled", on_toggle)
        box.pack_start(check, False, False, 0)

        hotkey_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hotkey_row.pack_start(Gtk.Label(label="Atalho global (mostrar/ocultar)"), False, False, 0)
        hotkey_value = Gtk.Label(label=self.settings.get("hotkey"))
        hotkey_value.get_style_context().add_class("dim-label")
        hotkey_row.pack_start(hotkey_value, False, False, 0)
        box.pack_start(hotkey_row, False, False, 0)

        # Estado real do registro -- não assumir sucesso silenciosamente
        # (achado P1 da revisão técnica).
        status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        if self.hotkey is not None and self.hotkey.bound:
            status_text = "✔ Ativo"
        else:
            status_text = "⚠ Não registrado (em uso por outro app, ou sem suporte no ambiente atual -- use a bandeja)"
        status_label = Gtk.Label(label=status_text)
        status_label.set_line_wrap(True)
        status_label.set_xalign(0.0)
        status_row.pack_start(status_label, True, True, 0)
        box.pack_start(status_row, False, False, 0)

        return frame

    def _on_close(self, *_a):
        self.hide()
        self.destroy()
        return False
