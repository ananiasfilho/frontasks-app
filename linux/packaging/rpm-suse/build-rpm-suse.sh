#!/usr/bin/env bash
# Frontasks — floating, always-on-top task list for Linux.
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

# Builda o .rpm do FronTasks para openSUSE Leap dentro de um container
# (nomes de dependencia diferem do Fedora -- ver o spec). Saida em
# packaging/rpm-suse/out/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="$SCRIPT_DIR/out"
mkdir -p "$OUT_DIR"

# Tag fixa para build reproduzivel.
SUSE_IMAGE="opensuse/leap:16.0"

docker run --rm \
  -v "$LINUX_DIR":/work:ro \
  -v "$OUT_DIR":/rpmbuild-out \
  "$SUSE_IMAGE" \
  bash -c '
    set -euo pipefail
    zypper --non-interactive --gpg-auto-import-keys refresh >/dev/null
    zypper --non-interactive install -y rpm-build python3 >/dev/null
    rpmbuild --define "_topdir /rpmbuild" \
             --define "_rpmdir /rpmbuild-out" \
             -bb /work/packaging/rpm-suse/frontasks.spec
  '

echo "OK -> $(find "$OUT_DIR" -name '*.rpm')"
