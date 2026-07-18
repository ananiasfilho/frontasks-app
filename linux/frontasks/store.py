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

"""Modelo TaskItem + TaskStore, persistidos em JSON (mesmo schema do Mac,
exceto createdAt que aqui usa epoch Unix -- ver README seção 9)."""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List

import gi
gi.require_version("GObject", "2.0")
from gi.repository import GObject

from .config import tasks_path
from .persistence import atomic_write_json, safe_load_json


@dataclass
class TaskItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    isDone: bool = False
    createdAt: float = field(default_factory=time.time)
    order: int = 0


def _validate_tasks(raw) -> List[TaskItem]:
    """Valida schema/tipos item a item. Um item individual inválido é
    descartado (não derruba a lista inteira); se `raw` não for nem uma
    lista, propaga a exceção pra safe_load_json tratar como corrupto."""
    if not isinstance(raw, list):
        raise ValueError("tasks.json: esperava uma lista")
    tasks = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            tasks.append(
                TaskItem(
                    id=str(item["id"]) if "id" in item else str(uuid.uuid4()),
                    title=str(item.get("title", "")),
                    isDone=bool(item.get("isDone", False)),
                    createdAt=float(item.get("createdAt", time.time())),
                    order=int(item.get("order", 0)),
                )
            )
        except (TypeError, ValueError):
            continue
    return tasks


class TaskStore(GObject.Object):
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()
        self.tasks: List[TaskItem] = []
        self._path = tasks_path()
        self.load()

    # --- Persistência -----------------------------------------------

    def load(self):
        tasks = safe_load_json(self._path, validate=_validate_tasks)
        if tasks is None:
            self.tasks = []
            return
        self.tasks = tasks
        self.tasks.sort(key=lambda t: (t.order, t.createdAt))

    def save(self):
        data = [asdict(t) for t in self.tasks]
        atomic_write_json(self._path, data)

    # --- CRUD ---------------------------------------------------------

    def add(self, title: str):
        title = title.strip()
        if not title:
            return
        max_order = max((t.order for t in self.tasks), default=0)
        self.tasks.append(TaskItem(title=title, order=max_order + 1))
        self.save()
        self.emit("changed")

    def toggle(self, task_id: str) -> bool:
        for t in self.tasks:
            if t.id == task_id:
                t.isDone = not t.isDone
                self.save()
                self.emit("changed")
                return True
        return False

    def update_title(self, task_id: str, title: str) -> bool:
        title = title.strip()
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                if not title:
                    del self.tasks[i]
                else:
                    t.title = title
                self.save()
                self.emit("changed")
                return True
        return False

    def delete(self, task_id: str) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) == before:
            return False
        self.save()
        self.emit("changed")
        return True

    def move(self, old_index: int, new_index: int) -> bool:
        if not (0 <= old_index < len(self.tasks)) or not (0 <= new_index < len(self.tasks)):
            return False
        if old_index == new_index:
            return False
        task = self.tasks.pop(old_index)
        self.tasks.insert(new_index, task)
        for i, t in enumerate(self.tasks):
            t.order = i
        self.save()
        self.emit("changed")
        return True

    def clear_completed(self):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.isDone]
        if len(self.tasks) == before:
            return
        self.save()
        self.emit("changed")

    @property
    def pending_count(self) -> int:
        return sum(1 for t in self.tasks if not t.isDone)

    @property
    def done_count(self) -> int:
        return sum(1 for t in self.tasks if t.isDone)
