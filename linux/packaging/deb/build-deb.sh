#!/usr/bin/env bash
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

# Builda um .deb standalone do FronTasks (pacote Python puro, sem
# compilação -- Architecture: all). Não usa debhelper/pybuild de propósito:
# o objetivo aqui é validar instalação em Debian/Ubuntu, não entrar em
# repositórios oficiais.
set -euo pipefail

VERSION="0.1.0"
ARCH="all"
PKG="frontasks"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
OUT="$SCRIPT_DIR/${PKG}_${VERSION}_${ARCH}.deb"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib/python3/dist-packages"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"

cp -r "$LINUX_DIR/frontasks" "$BUILD_DIR/usr/lib/python3/dist-packages/"
find "$BUILD_DIR/usr/lib/python3/dist-packages/frontasks" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cp "$LINUX_DIR/data/frontasks.desktop" "$BUILD_DIR/usr/share/applications/"
cp "$LINUX_DIR/frontasks/data/icons/frontasks.png" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/"

cat > "$BUILD_DIR/usr/bin/frontasks" <<'EOF'
#!/usr/bin/env python3
import sys
from frontasks.__main__ import main
sys.exit(main())
EOF
chmod 755 "$BUILD_DIR/usr/bin/frontasks"

cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: $PKG
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-keybinder-3.0, gir1.2-xapp-1.0
Maintainer: Ananias Filho <kram3r@gmail.com>
Homepage: https://github.com/ananiasfilho/frontasks-app
Description: Painel de tarefas flutuante e sempre-no-topo
 FronTasks e um painel de tarefas leve, sempre-no-topo, com bandeja e
 atalho global, para Linux (GTK3). Porte do app macOS original.
EOF

cat > "$BUILD_DIR/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications >/dev/null 2>&1 || true
fi
exit 0
EOF
chmod 755 "$BUILD_DIR/DEBIAN/postinst"

find "$BUILD_DIR" -type d -exec chmod 755 {} +
find "$BUILD_DIR" -type f -not -path "*/DEBIAN/postinst" -not -path "*/usr/bin/frontasks" -exec chmod 644 {} +

dpkg-deb --build --root-owner-group "$BUILD_DIR" "$OUT"
echo "OK -> $OUT"
