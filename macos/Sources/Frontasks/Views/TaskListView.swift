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

/// Conteúdo do painel flutuante: cabeçalho, lista e barra de nova tarefa.
struct TaskListView: View {
    @EnvironmentObject private var store: TaskStore

    @AppStorage("accentHex") private var accentHex = "#3B82F6"
    @AppStorage("bgHex") private var bgHex = "#2C2C2E"
    @AppStorage("bgOpacity") private var bgOpacity = 0.55
    @AppStorage("fontName") private var fontName = "System"
    @AppStorage("fontSize") private var fontSize = 14.0
    @AppStorage("textHex") private var textHex = "auto"

    @State private var newTitle = ""
    @FocusState private var inputFocused: Bool

    private var accent: Color { Color(hex: accentHex) }
    private var uiFont: Font { appFont(fontName, fontSize) }

    var body: some View {
        VStack(spacing: 0) {
            header
            Divider()
            list
            Divider()
            inputBar
        }
        .frame(minWidth: 240, minHeight: 200)
        .background {
            ZStack {
                Rectangle().fill(.regularMaterial)          // borrão/vidro por baixo
                Rectangle().fill(Color(hex: bgHex).opacity(bgOpacity)) // tinta escolhida
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(Color.primary.opacity(0.08), lineWidth: 1)
        )
        .tint(accent)
    }

    private var header: some View {
        HStack(spacing: 6) {
            Image(systemName: "checklist").foregroundStyle(accent)
            Text("Frontasks").font(.headline)
            Spacer()
            if store.pendingCount > 0 {
                Text("\(store.pendingCount)")
                    .font(.caption.monospacedDigit())
                    .foregroundStyle(.secondary)
            }
            if store.doneCount > 0 {
                Button {
                    store.clearCompleted()
                } label: {
                    Image(systemName: "eraser")
                }
                .buttonStyle(.plain)
                .foregroundStyle(.secondary)
                .help("Limpar \(store.doneCount) concluída(s)")
            }
            Button {
                openSettingsWindow()
            } label: {
                Image(systemName: "gearshape")
            }
            .buttonStyle(.plain)
            .foregroundStyle(.secondary)
            .help("Ajustes")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .contentShape(Rectangle()) // área de arraste do painel
    }

    @ViewBuilder
    private var list: some View {
        if store.tasks.isEmpty {
            VStack {
                Spacer()
                Text("Sem tarefas ainda.\nEscreva abaixo para começar.")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            List {
                ForEach(store.tasks) { task in
                    TaskRow(task: task, accent: accent, font: uiFont)
                        .listRowInsets(EdgeInsets(top: 1, leading: 8, bottom: 1, trailing: 8))
                        .listRowBackground(Color.clear)
                        .listRowSeparator(.hidden)
                }
                .onMove(perform: store.move)
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
        }
    }

    private var inputBar: some View {
        HStack(spacing: 8) {
            Image(systemName: "plus").foregroundStyle(.secondary)
            TextField("Nova tarefa…", text: $newTitle)
                .textFieldStyle(.plain)
                .font(uiFont)
                .foregroundStyle(textColor(textHex))
                .focused($inputFocused)
                .onSubmit(add)
            if !newTitle.trimmingCharacters(in: .whitespaces).isEmpty {
                Button(action: add) {
                    Image(systemName: "return").foregroundStyle(accent)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
    }

    private func add() {
        store.add(newTitle)
        newTitle = ""
        inputFocused = true
    }
}
