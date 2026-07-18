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

"""Escrita atômica e leitura defensiva de JSON.

Usado por store.py, settings.py e panel.py (geometria) -- ver achados P0 da
revisão técnica (analista-revisor.md): escrita direta no arquivo final pode
truncar dados numa interrupção, e falta de validação de schema derruba o
app inteiro se o arquivo tiver a forma errada.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("frontasks.persistence")


def atomic_write_json(path: Path, data: Any) -> None:
    """Grava em arquivo temporário no mesmo diretório, fsync, e substitui
    o arquivo final via os.replace (atômico no mesmo filesystem) -- uma
    interrupção no meio do caminho nunca deixa o arquivo final truncado."""
    tmp = path.with_suffix(path.suffix + f".tmp-{os.getpid()}")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except OSError:
        logger.exception("Falha ao gravar %s", path)
        tmp.unlink(missing_ok=True)
        raise


def safe_load_json(
    path: Path, validate: Optional[Callable[[Any], Any]] = None
) -> Optional[Any]:
    """Lê e faz parse de `path`. Se o arquivo não existir, retorna None
    (chamador usa defaults). Se existir mas estiver corrompido ou não
    passar em `validate`, preserva o original como `<path>.corrupt-<ts>`
    (não descarta silenciosamente -- dá pra investigar depois) e retorna
    None."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    try:
        data = json.loads(raw)
        if validate is not None:
            data = validate(data)
        return data
    except Exception:
        logger.exception("Arquivo inválido, preservando como .corrupt: %s", path)
        corrupt_path = path.with_name(f"{path.name}.corrupt-{int(time.time())}")
        try:
            path.replace(corrupt_path)
        except OSError:
            logger.exception("Não consegui preservar %s como %s", path, corrupt_path)
        return None
