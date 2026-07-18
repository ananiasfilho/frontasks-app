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

# Builda o .rpm do FronTasks dentro de um container Fedora (o host não tem
# rpmbuild instalado). Saída fica em packaging/rpm/out/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINUX_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="$SCRIPT_DIR/out"
mkdir -p "$OUT_DIR"

# Tag fixa (não "latest") para build reproduzível -- achado da revisão
# técnica. Atualize aqui deliberadamente quando quiser mudar de versão.
FEDORA_IMAGE="fedora:44"

docker run --rm \
  -v "$LINUX_DIR":/work:ro \
  -v "$OUT_DIR":/rpmbuild-out \
  "$FEDORA_IMAGE" \
  bash -c '
    set -euo pipefail
    dnf install -y -q rpm-build python3-devel >/dev/null
    rpmbuild --define "_topdir /rpmbuild" \
             --define "_rpmdir /rpmbuild-out" \
             -bb /work/packaging/rpm/frontasks.spec
  '

echo "OK -> $(find "$OUT_DIR" -name '*.rpm')"
