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
import Carbon.HIToolbox

/// Atalho global do sistema (⌥Espaço) para mostrar/ocultar o painel.
/// Usa Carbon `RegisterEventHotKey` — funciona mesmo com o app em segundo
/// plano e NÃO exige permissão de Acessibilidade.
@MainActor
final class HotKeyManager {
    static let shared = HotKeyManager()
    private var hotKeyRef: EventHotKeyRef?
    private var installed = false

    private init() {}

    func registerDefault() {
        guard !installed else { return }
        installed = true

        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: UInt32(kEventHotKeyPressed)
        )
        InstallEventHandler(GetApplicationEventTarget(), { _, _, _ -> OSStatus in
            DispatchQueue.main.async { PanelController.shared.toggle() }
            return noErr
        }, 1, &eventType, nil, nil)

        // ⌥ (option) + Espaço. Para trocar: mude optionKey / kVK_Space abaixo.
        let hotKeyID = EventHotKeyID(signature: OSType(0x46524B59), id: 1) // 'FRKY'
        RegisterEventHotKey(
            UInt32(kVK_Space),
            UInt32(optionKey),
            hotKeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )
    }
}
