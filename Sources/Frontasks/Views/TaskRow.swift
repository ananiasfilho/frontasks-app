//  Frontasks — floating, always-on-top task list for macOS.
//  Copyright (C) 2026 Ananias Filho
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU Affero General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Affero General Public License for more details.
//
//  You should have received a copy of the GNU Affero General Public License
//  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import SwiftUI

/// Uma linha da lista: concluir, editar inline e apagar.
struct TaskRow: View {
    @EnvironmentObject private var store: TaskStore
    let task: TaskItem
    let accent: Color
    let font: Font

    @State private var hovering = false

    private var titleBinding: Binding<String> {
        Binding(
            get: { task.title },
            set: { store.updateTitle(task.id, $0) }
        )
    }

    var body: some View {
        HStack(spacing: 8) {
            Button {
                store.toggle(task.id)
            } label: {
                Image(systemName: task.isDone ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(task.isDone ? accent : .secondary)
                    .imageScale(.large)
            }
            .buttonStyle(.plain)

            TextField("", text: titleBinding)
                .textFieldStyle(.plain)
                .font(font)
                .strikethrough(task.isDone)
                .foregroundStyle(task.isDone ? .secondary : .primary)

            if hovering {
                Button {
                    store.delete(task.id)
                } label: {
                    Image(systemName: "trash")
                        .foregroundStyle(.red.opacity(0.85))
                }
                .buttonStyle(.plain)
                .help("Apagar tarefa")
            }
        }
        .padding(.vertical, 5)
        .padding(.horizontal, 8)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(hovering ? Color.primary.opacity(0.06) : Color.clear)
        )
        .onHover { hovering = $0 }
    }
}
