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
import AppKit
import ServiceManagement

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
        // Comandos one-shot de manutenção do item de login (suporte/limpeza):
        //   open Frontasks.app --args --login-off  → remove ESTE app do início no login
        //   open Frontasks.app --args --login-on   → registra ESTE app no início no login
        if CommandLine.arguments.contains("--login-off") {
            try? SMAppService.mainApp.unregister()
            NSApp.terminate(nil); return
        }
        if CommandLine.arguments.contains("--login-on") {
            try? SMAppService.mainApp.register()
            NSApp.terminate(nil); return
        }

        // Instância única: se já houver OUTRO Frontasks rodando (ex.: uma segunda
        // cópia do .app registrada no login, ou restauração de sessão do macOS),
        // ativa o existente e encerra esta. Garante que nunca haja dois painéis.
        let myID = Bundle.main.bundleIdentifier ?? "com.ananiasfilho.frontasks"
        let others = NSRunningApplication.runningApplications(withBundleIdentifier: myID)
            .filter { $0 != .current }
        if !others.isEmpty {
            others.first?.activate()
            NSApp.terminate(nil)
            return
        }

        HotKeyManager.shared.registerDefault()

        // `open -n Frontasks.app --args --settings` abre direto os Ajustes,
        // SEM exibir o painel.
        if CommandLine.arguments.contains("--settings") {
            PanelController.shared.showSettings()
        } else {
            PanelController.shared.showPanel()
        }
    }

    /// Grava qualquer edição pendente (debounced) antes de encerrar.
    func applicationWillTerminate(_ notification: Notification) {
        TaskStore.shared.save()
    }
}
