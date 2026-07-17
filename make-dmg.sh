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

# Empacota o Frontasks.app num .dmg de instalacao (arraste para Applications).
set -eo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_NAME="Frontasks"
VERSION="${1:-0.1.0}"
APP="$ROOT/$APP_NAME.app"
DMG="$ROOT/dist/$APP_NAME-$VERSION.dmg"

echo "Compilando o app..."
./make-app.sh >/dev/null

STAGE="$(mktemp -d)"
cp -R "$APP" "$STAGE/$APP_NAME.app"
ln -s /Applications "$STAGE/Applications"

mkdir -p "$ROOT/dist"
rm -f "$DMG"

echo "Gerando $DMG ..."
hdiutil create -volname "$APP_NAME" -srcfolder "$STAGE" -fs HFS+ -format UDZO -ov "$DMG" >/dev/null

rm -rf "$STAGE"
codesign --force --sign - "$DMG" 2>/dev/null || true

echo "Pronto: $DMG"
ls -lh "$DMG" | awk '{print "Tamanho: " $5}'
