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

/// Fonte da UI a partir das preferências. "System" usa a fonte do sistema.
func appFont(_ name: String, _ size: Double) -> Font {
    name == "System" ? .system(size: size) : .custom(name, size: size)
}

/// Abre a janela de Ajustes trazendo o app (accessory) para a frente.
@MainActor
func openSettingsWindow() {
    PanelController.shared.showSettings()
}

/// Paleta de cores de fundo do cartão (nome, hex).
let backgroundPresets: [(name: String, hex: String)] = [
    ("Grafite",     "#2C2C2E"),
    ("Cinza",       "#48484A"),
    ("Azul-noite",  "#1E293B"),
    ("Verde-musgo", "#14342B"),
    ("Vinho",       "#3B1D2B"),
    ("Roxo escuro", "#241B36"),
    ("Areia",       "#EAE0D5"),
    ("Branco",      "#FFFFFF"),
]

/// Paleta de cores de destaque pré-definidas (nome, hex).
let accentPresets: [(name: String, hex: String)] = [
    ("Azul",      "#3B82F6"),
    ("Índigo",    "#6366F1"),
    ("Roxo",      "#8B5CF6"),
    ("Rosa",      "#EC4899"),
    ("Vermelho",  "#EF4444"),
    ("Laranja",   "#F97316"),
    ("Amarelo",   "#EAB308"),
    ("Verde",     "#22C55E"),
    ("Turquesa",  "#14B8A6"),
    ("Grafite",   "#6B7280"),
]

extension Color {
    /// Cria uma cor a partir de um hex "#RRGGBB".
    init(hex: String) {
        let s = hex.trimmingCharacters(in: CharacterSet(charactersIn: "# "))
        var v: UInt64 = 0
        Scanner(string: s).scanHexInt64(&v)
        if s.count == 6 {
            let r = Double((v >> 16) & 0xFF) / 255
            let g = Double((v >> 8) & 0xFF) / 255
            let b = Double(v & 0xFF) / 255
            self = Color(red: r, green: g, blue: b)
        } else {
            self = Color(red: 0.23, green: 0.51, blue: 0.96) // azul padrão
        }
    }

    /// Serializa para "#RRGGBB" (para guardar em @AppStorage).
    var hexString: String {
        let ns = NSColor(self).usingColorSpace(.sRGB) ?? NSColor.systemBlue
        return String(format: "#%02X%02X%02X",
                      Int(round(ns.redComponent * 255)),
                      Int(round(ns.greenComponent * 255)),
                      Int(round(ns.blueComponent * 255)))
    }
}
