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

"""Atalho global via Keybinder (equivalente a HotKeyManager.swift)."""

import gi

gi.require_version("Keybinder", "3.0")
from gi.repository import Keybinder

_initialized = False


def _ensure_init():
    global _initialized
    if not _initialized:
        Keybinder.init()
        _initialized = True


class HotkeyManager:
    def __init__(self, accel: str, callback):
        _ensure_init()
        self.accel = accel
        self.callback = callback
        self.bound = False

    def bind(self) -> bool:
        if self.bound:
            return True
        ok = Keybinder.bind(self.accel, lambda _keystring, _data: self.callback(), None)
        self.bound = bool(ok)
        return self.bound

    def unbind(self):
        if self.bound:
            Keybinder.unbind(self.accel)
            self.bound = False

    def rebind(self, new_accel: str) -> bool:
        self.unbind()
        self.accel = new_accel
        return self.bind()
