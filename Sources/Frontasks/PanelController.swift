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

/// Dono do painel flutuante. Cria sob demanda e alterna visibilidade.
@MainActor
final class PanelController: ObservableObject {
    static let shared = PanelController()
    private var panel: FloatingPanel?
    private var settingsWindow: NSWindow?

    private init() {}

    /// Abre (ou traz pra frente) a janela de Ajustes, gerenciada via AppKit.
    func showSettings() {
        NSApp.activate(ignoringOtherApps: true)
        if settingsWindow == nil {
            let w = NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 400, height: 600),
                styleMask: [.titled, .closable, .resizable],
                backing: .buffered,
                defer: false
            )
            w.title = "Ajustes do Frontasks"
            w.isReleasedWhenClosed = false
            w.level = .floating // garante que apareça acima do painel flutuante
            w.minSize = NSSize(width: 380, height: 460)
            w.contentView = NSHostingView(rootView: SettingsView())
            w.setFrameAutosaveName("FrontasksSettings") // lembra o tamanho
            if !w.setFrameUsingName("FrontasksSettings") {
                w.center()
            }
            settingsWindow = w
        }
        settingsWindow?.makeKeyAndOrderFront(nil)
        settingsWindow?.orderFrontRegardless()
    }

    func showPanel() {
        if panel == nil {
            let p = FloatingPanel(contentRect: NSRect(x: 0, y: 0, width: 300, height: 420))
            let root = TaskListView()
                .environmentObject(TaskStore.shared)
            let host = NSHostingView(rootView: root)
            host.autoresizingMask = [NSView.AutoresizingMask.width, .height]
            p.contentView = host

            // Req 1: restaura a última posição/tamanho salvos.
            // Req 2: se for a primeira vez (nada salvo), abre no canto
            // superior direito do monitor central.
            if !p.setFrameUsingName(FloatingPanel.autosaveName) {
                positionTopRight(p)
            }
            panel = p
        }
        panel?.makeKeyAndOrderFront(nil)
    }

    /// Posiciona a janela no canto superior direito do monitor "central".
    private func positionTopRight(_ window: NSWindow) {
        let screens = NSScreen.screens
        guard !screens.isEmpty else { window.center(); return }

        // Monitor central = tela que contém o centro da união de todas as telas.
        let union = screens.reduce(screens[0].frame) { $0.union($1.frame) }
        let center = NSPoint(x: union.midX, y: union.midY)
        let central = screens.first { NSMouseInRect(center, $0.frame, false) }
            ?? NSScreen.main
            ?? screens[0]

        let vf = central.visibleFrame // desconta menu bar e Dock
        let margin: CGFloat = 16
        let size = window.frame.size
        let origin = NSPoint(
            x: vf.maxX - size.width - margin,
            y: vf.maxY - size.height - margin
        )
        window.setFrameOrigin(origin)
        window.saveFrame(usingName: FloatingPanel.autosaveName)
    }

    func toggle() {
        guard let panel else { showPanel(); return }
        if panel.isVisible {
            panel.orderOut(nil)
        } else {
            panel.makeKeyAndOrderFront(nil)
        }
    }
}
