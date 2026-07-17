#!/bin/bash
# Frontasks — floating, always-on-top task list for macOS.
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
# Gera o ícone do app (Icon/icon.icns) a partir da arte desenhada em Tools/makeicon.swift.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p Icon

echo "▸ Renderizando arte 1024×1024…"
swift Tools/makeicon.swift

SRC="Icon/icon_1024.png"
SET="Icon/AppIcon.iconset"
rm -rf "$SET"; mkdir -p "$SET"

gen() { sips -z "$1" "$1" "$SRC" --out "$SET/$2" >/dev/null; }
gen 16  icon_16x16.png
gen 32  icon_16x16@2x.png
gen 32  icon_32x32.png
gen 64  icon_32x32@2x.png
gen 128 icon_128x128.png
gen 256 icon_128x128@2x.png
gen 256 icon_256x256.png
gen 512 icon_256x256@2x.png
gen 512 icon_512x512.png
cp "$SRC" "$SET/icon_512x512@2x.png"

echo "▸ Compilando icon.icns…"
iconutil -c icns "$SET" -o Icon/icon.icns
echo "✓ Icon/icon.icns pronto"
