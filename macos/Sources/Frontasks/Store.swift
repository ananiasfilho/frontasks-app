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

import Foundation
import Combine

/// Uma tarefa da lista.
struct TaskItem: Identifiable, Codable, Equatable {
    var id: UUID = UUID()
    var title: String
    var isDone: Bool = false
    var createdAt: Date = .now
    var order: Int = 0
}

/// Store observável, persistida em JSON dentro de Application Support.
@MainActor
final class TaskStore: ObservableObject {
    static let shared = TaskStore()

    @Published var tasks: [TaskItem] = []

    private let url: URL
    private var saveWork: DispatchWorkItem?

    private init() {
        let dir = FileManager.default
            .urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("Frontasks", isDirectory: true)
        do {
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        } catch {
            NSLog("Frontasks: falha ao criar a pasta de dados — \(error).")
        }
        url = dir.appendingPathComponent("tasks.json")
        load()
    }

    // MARK: - Persistência

    func load() {
        // Primeiro uso: arquivo ainda não existe — lista vazia, sem erro.
        guard FileManager.default.fileExists(atPath: url.path) else { return }
        do {
            let data = try Data(contentsOf: url)
            let decoded = try JSONDecoder().decode([TaskItem].self, from: data)
            tasks = decoded.sorted { ($0.order, $0.createdAt) < ($1.order, $1.createdAt) }
        } catch {
            // P0: NÃO destruir o arquivo do usuário. Preserva o inválido antes que
            // qualquer save() (inclusive o flush no encerramento) o sobrescreva com [].
            backupCorruptStore(error)
        }
    }

    /// Faz backup de um `tasks.json` inválido para não perder as tarefas do usuário.
    private func backupCorruptStore(_ error: Error) {
        let fmt = DateFormatter()
        fmt.dateFormat = "yyyy-MM-dd-HHmmss"
        let backup = url.deletingLastPathComponent()
            .appendingPathComponent("tasks.corrupt-\(fmt.string(from: Date())).json")
        try? FileManager.default.copyItem(at: url, to: backup)
        NSLog("Frontasks: tasks.json inválido (\(error)). Backup preservado em \(backup.lastPathComponent). Iniciando com lista vazia.")
    }

    /// Grava imediatamente (operações pontuais e no encerramento do app).
    func save() {
        saveWork?.cancel()
        saveWork = nil
        do {
            let data = try JSONEncoder().encode(tasks)
            try data.write(to: url, options: .atomic)
        } catch {
            NSLog("Frontasks: falha ao gravar tasks.json — \(error).")
        }
    }

    /// Grava com pequeno atraso — para edição de texto (evita escrever a cada tecla).
    private func saveDebounced() {
        saveWork?.cancel()
        let work = DispatchWorkItem { [weak self] in self?.save() }
        saveWork = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4, execute: work)
    }

    // MARK: - CRUD

    func add(_ title: String) {
        let trimmed = title.trimmingCharacters(in: .whitespaces)
        guard !trimmed.isEmpty else { return }
        let maxOrder = tasks.map(\.order).max() ?? 0
        tasks.append(TaskItem(title: trimmed, order: maxOrder + 1))
        save()
    }

    func toggle(_ id: UUID) {
        guard let i = tasks.firstIndex(where: { $0.id == id }) else { return }
        tasks[i].isDone.toggle()
        save()
    }

    func updateTitle(_ id: UUID, _ title: String) {
        guard let i = tasks.firstIndex(where: { $0.id == id }) else { return }
        tasks[i].title = title
        saveDebounced()
    }

    /// Finaliza a edição de um título: remove espaços das pontas e, se ficar vazio,
    /// apaga a tarefa. Deve ser chamado no commit (Enter/perda de foco), NUNCA a cada tecla.
    func commitTitle(_ id: UUID) {
        guard let i = tasks.firstIndex(where: { $0.id == id }) else { return }
        let trimmed = tasks[i].title.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            tasks.remove(at: i)
        } else {
            tasks[i].title = trimmed
        }
        save()
    }

    func delete(_ id: UUID) {
        tasks.removeAll { $0.id == id }
        save()
    }

    /// Reordena (arrastar) e reatribui `order` para persistir a nova sequência.
    func move(from source: IndexSet, to destination: Int) {
        tasks.move(fromOffsets: source, toOffset: destination)
        for i in tasks.indices { tasks[i].order = i }
        save()
    }

    /// Remove de uma vez todas as tarefas concluídas.
    func clearCompleted() {
        tasks.removeAll { $0.isDone }
        save()
    }

    var pendingCount: Int { tasks.filter { !$0.isDone }.count }
    var doneCount: Int { tasks.filter { $0.isDone }.count }
}
