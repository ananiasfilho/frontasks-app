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

import AppKit

/// Painel flutuante, redimensionável, que fica sobre as janelas normais
/// sem roubar o foco do app onde você está trabalhando.
final class FloatingPanel: NSPanel {
    static let autosaveName = "FrontasksPanel"

    init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .fullSizeContentView, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )

        isFloatingPanel = true
        level = .floating                       // acima das janelas normais
        collectionBehavior = [.canJoinAllSpaces, // aparece em todos os Spaces
                              .stationary]        // não desliza no Mission Control

        // Aparência de "cartão" sem chrome: sem barra de título visível.
        titleVisibility = .hidden
        titlebarAppearsTransparent = true
        isMovableByWindowBackground = true       // arrasta pelo fundo
        backgroundColor = .clear

        hidesOnDeactivate = false                // não some quando outro app ganha foco
        isReleasedWhenClosed = false

        // Esconde os botões de semáforo — controle é pelo ícone da barra de menus.
        [.closeButton, .miniaturizeButton, .zoomButton].forEach {
            standardWindowButton($0)?.isHidden = true
        }

        minSize = NSSize(width: 240, height: 200)
        setFrameAutosaveName(FloatingPanel.autosaveName)  // lembra tamanho e posição
    }

    // Permite editar texto (campo de nova tarefa / edição inline) mesmo sem ativar o app.
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { false }
}
