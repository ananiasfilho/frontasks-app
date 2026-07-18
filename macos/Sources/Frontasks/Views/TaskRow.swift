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

    @AppStorage("textHex") private var textHex = "auto"
    @State private var hovering = false
    @FocusState private var focused: Bool

    private var itemColor: Color { textColor(textHex) }

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
                .foregroundStyle(task.isDone ? itemColor.opacity(0.45) : itemColor)
                .focused($focused)
                .onSubmit { store.commitTitle(task.id) }
                .onChange(of: focused) { _, isFocused in
                    if !isFocused { store.commitTitle(task.id) }  // apaga se ficou vazio
                }

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
        .contextMenu {
            Button(task.isDone ? "Reabrir" : "Concluir") { store.toggle(task.id) }
            Button("Apagar", role: .destructive) { store.delete(task.id) }
        }
    }
}
