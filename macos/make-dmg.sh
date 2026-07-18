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

# Empacota o Frontasks.app num .dmg de instalacao com janela estilizada
# (fundo com seta + icones posicionados, arraste para Applications).
set -eo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_NAME="Frontasks"
VERSION="${1:-0.1.2}"
APP="$ROOT/$APP_NAME.app"
DMG="$ROOT/dist/$APP_NAME-$VERSION.dmg"

echo "Compilando o app (versão $VERSION)..."
./make-app.sh "$VERSION" >/dev/null

# Fundo da janela.
BGDIR="$(mktemp -d)"
swift Tools/makedmgbg.swift "$BGDIR/bg.png" >/dev/null

# Estrutura da janela: app + atalho Applications + fundo oculto.
STAGE="$(mktemp -d)"
cp -R "$APP" "$STAGE/$APP_NAME.app"
ln -s /Applications "$STAGE/Applications"
mkdir "$STAGE/.background"
cp "$BGDIR/bg.png" "$STAGE/.background/bg.png"

mkdir -p "$ROOT/dist"
rm -f "$DMG"

# Desmonta um volume anterior, se existir.
[ -d "/Volumes/$APP_NAME" ] && hdiutil detach "/Volumes/$APP_NAME" -force >/dev/null 2>&1 || true

# DMG read-write temporario.
TMPDMG="$(mktemp -u).dmg"
hdiutil create -volname "$APP_NAME" -srcfolder "$STAGE" -fs HFS+ -format UDRW -ov "$TMPDMG" >/dev/null

MP="$(hdiutil attach "$TMPDMG" -nobrowse -noautoopen | awk -F'\t' '/Volumes/{print $NF}')"
VOL="$(basename "$MP")"
sleep 1

# Layout via Finder (nao-fatal: se a Automacao for bloqueada, segue sem estilo).
set +e
osascript <<APPLESCRIPT
tell application "Finder"
  tell disk "$VOL"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set the bounds of container window to {400, 150, 1040, 550}
    set opts to the icon view options of container window
    set arrangement of opts to not arranged
    set icon size of opts to 128
    set text size of opts to 13
    set background picture of opts to file ".background:bg.png"
    set position of item "$APP_NAME.app" of container window to {170, 205}
    set position of item "Applications" of container window to {470, 205}
    update without registering applications
    delay 1
    close
  end tell
end tell
APPLESCRIPT
LAYOUT=$?
set -e
if [ $LAYOUT -ne 0 ]; then
  echo "AVISO: layout do Finder nao aplicado (permissao de Automacao?). DMG sai funcional, sem estilo."
fi

sync
hdiutil detach "$MP" -force >/dev/null 2>&1 || hdiutil detach "$MP" >/dev/null 2>&1 || true

# Converte para comprimido (somente leitura).
hdiutil convert "$TMPDMG" -format UDZO -imagekey zlib-level=9 -o "$DMG" >/dev/null
rm -f "$TMPDMG"
rm -rf "$STAGE" "$BGDIR"

codesign --force --sign - "$DMG" 2>/dev/null || true

echo "Pronto: $DMG"
ls -lh "$DMG" | awk '{print "Tamanho: " $5}'
