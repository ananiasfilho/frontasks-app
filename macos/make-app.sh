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
# Compila o Frontasks e empacota em Frontasks.app (assinatura ad-hoc, uso local).
set -euo pipefail

APP_NAME="Frontasks"
BUNDLE_ID="com.ananiasfilho.frontasks"
VERSION="${1:-0.1.1}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Compilando (release) - versao ${VERSION}..."
swift build -c release

BIN="$ROOT/.build/release/$APP_NAME"
APP="$ROOT/$APP_NAME.app"

echo "▸ Empacotando $APP_NAME.app…"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/$APP_NAME"

if [ -f "$ROOT/Icon/icon.icns" ]; then
    cp "$ROOT/Icon/icon.icns" "$APP/Contents/Resources/icon.icns"
else
    echo "  (aviso: Icon/icon.icns não encontrado — rode ./make-icon.sh)"
fi

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>$APP_NAME</string>
    <key>CFBundleDisplayName</key><string>$APP_NAME</string>
    <key>CFBundleIdentifier</key><string>$BUNDLE_ID</string>
    <key>CFBundleExecutable</key><string>$APP_NAME</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleIconFile</key><string>icon</string>
    <key>CFBundleIconName</key><string>icon</string>
    <key>CFBundleShortVersionString</key><string>$VERSION</string>
    <key>CFBundleVersion</key><string>$VERSION</string>
    <key>LSMinimumSystemVersion</key><string>15.0</string>
    <key>LSUIElement</key><true/>
    <key>NSHumanReadableCopyright</key><string>© 2026 Ananias Filho</string>
</dict>
</plist>
PLIST

echo "▸ Assinando (ad-hoc)…"
codesign --force --deep --sign - "$APP"

echo "✓ Pronto: $APP"
echo "  Rodar com:  open \"$APP\""
