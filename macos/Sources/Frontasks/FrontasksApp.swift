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

@main
struct FrontasksApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var delegate

    var body: some Scene {
        MenuBarExtra("Frontasks", systemImage: "checklist") {
            Button("Mostrar / ocultar lista  (Option/Alt + Espaço)") {
                PanelController.shared.toggle()
            }
            Button("Ajustes…") { openSettingsWindow() }
                .keyboardShortcut(",")
            Divider()
            Button("Sair do Frontasks") { NSApplication.shared.terminate(nil) }
                .keyboardShortcut("q")
        }
    }
}

/// Cria o painel assim que o app termina de iniciar.
final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        PanelController.shared.showPanel()
        HotKeyManager.shared.registerDefault()

        // Permite abrir direto os Ajustes: `open -n Frontasks.app --args --settings`
        if CommandLine.arguments.contains("--settings") {
            PanelController.shared.showSettings()
        }
    }
}
