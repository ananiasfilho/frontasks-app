//  FronTasks — floating, always-on-top task list for macOS.
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

/// Tela de Ajustes: cor de destaque, fonte, tamanho e iniciar no login.
struct SettingsView: View {
    @AppStorage("accentHex") private var accentHex = "#3B82F6"
    @AppStorage("bgHex") private var bgHex = "#2C2C2E"
    @AppStorage("bgOpacity") private var bgOpacity = 0.55
    @AppStorage("textHex") private var textHex = "auto"
    @AppStorage("fontName") private var fontName = "System"
    @AppStorage("fontSize") private var fontSize = 14.0

    private let families: [String] = ["System"] + NSFontManager.shared.availableFontFamilies

    private var customColorBinding: Binding<Color> {
        Binding(
            get: { Color(hex: accentHex) },
            set: { accentHex = $0.hexString }
        )
    }

    private var customBgBinding: Binding<Color> {
        Binding(
            get: { Color(hex: bgHex) },
            set: { bgHex = $0.hexString }
        )
    }

    private var customTextBinding: Binding<Color> {
        Binding(
            get: { textColor(textHex) },
            set: { textHex = $0.hexString }
        )
    }

    private func isSelected(_ hex: String, _ current: String) -> Bool {
        current.caseInsensitiveCompare(hex) == .orderedSame
    }

    /// Swatch para a cor do texto — trata "auto" com um visual meio-a-meio.
    @ViewBuilder
    private func textSwatch(_ hex: String) -> some View {
        let selected = isSelected(hex, textHex)
        Circle()
            .fill(hex == "auto"
                  ? AnyShapeStyle(LinearGradient(colors: [.white, .black],
                                                 startPoint: .topLeading, endPoint: .bottomTrailing))
                  : AnyShapeStyle(Color(hex: hex)))
            .frame(width: 26, height: 26)
            .overlay(Circle().strokeBorder(Color.primary.opacity(0.15), lineWidth: 1))
            .overlay(Circle().strokeBorder(Color.primary.opacity(selected ? 0.9 : 0), lineWidth: 2).padding(-3))
            .contentShape(Circle())
            .onTapGesture { textHex = hex }
    }

    private func swatch(_ hex: String, current: String, action: @escaping () -> Void) -> some View {
        Circle()
            .fill(Color(hex: hex))
            .frame(width: 26, height: 26)
            .overlay(Circle().strokeBorder(Color.primary.opacity(0.15), lineWidth: 1))
            .overlay(
                Circle().strokeBorder(
                    Color.primary.opacity(isSelected(hex, current) ? 0.9 : 0),
                    lineWidth: 2
                )
                .padding(-3)
            )
            .contentShape(Circle())
            .onTapGesture(perform: action)
    }

    var body: some View {
        Form {
            Section("Fundo do cartão") {
                LazyVGrid(
                    columns: [GridItem(.adaptive(minimum: 30), spacing: 12)],
                    spacing: 12
                ) {
                    ForEach(backgroundPresets, id: \.hex) { preset in
                        swatch(preset.hex, current: bgHex) { bgHex = preset.hex }
                            .help(preset.name)
                    }
                }
                .padding(.vertical, 4)

                ColorPicker("Personalizada…", selection: customBgBinding, supportsOpacity: false)

                HStack {
                    Text("Transparência")
                    Slider(value: $bgOpacity, in: 0.1...1.0)
                    Text("\(Int(bgOpacity * 100))%")
                        .monospacedDigit()
                        .foregroundStyle(.secondary)
                        .frame(width: 44, alignment: .trailing)
                }
            }

            Section("Cor de destaque") {
                LazyVGrid(
                    columns: [GridItem(.adaptive(minimum: 30), spacing: 12)],
                    spacing: 12
                ) {
                    ForEach(accentPresets, id: \.hex) { preset in
                        swatch(preset.hex, current: accentHex) { accentHex = preset.hex }
                            .help(preset.name)
                    }
                }
                .padding(.vertical, 4)

                ColorPicker("Personalizada…", selection: customColorBinding, supportsOpacity: false)
            }

            Section("Cor do texto") {
                LazyVGrid(
                    columns: [GridItem(.adaptive(minimum: 30), spacing: 12)],
                    spacing: 12
                ) {
                    ForEach(textPresets, id: \.hex) { preset in
                        textSwatch(preset.hex)
                            .help(preset.name)
                    }
                }
                .padding(.vertical, 4)

                ColorPicker("Personalizada…", selection: customTextBinding, supportsOpacity: false)
            }

            Section("Fonte") {
                Picker("Família", selection: $fontName) {
                    ForEach(families, id: \.self) { fam in
                        Text(fam).tag(fam)
                    }
                }

                HStack {
                    Text("Tamanho")
                    Slider(value: $fontSize, in: 10...28, step: 1)
                    Text("\(Int(fontSize)) pt")
                        .monospacedDigit()
                        .foregroundStyle(.secondary)
                        .frame(width: 44, alignment: .trailing)
                }

                // Prévia
                HStack(spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundStyle(Color(hex: accentHex))
                    Text("Exemplo de tarefa")
                        .font(appFont(fontName, fontSize))
                }
                .padding(.vertical, 2)
            }

            Section("Sistema") {
                // O estado do toggle vem do sistema (SMAppService), então reflete
                // a realidade — se registrar/desregistrar falhar, ele reverte sozinho.
                Toggle("Iniciar ao ligar o Mac", isOn: Binding(
                    get: { SMAppService.mainApp.status == .enabled },
                    set: { setLaunchAtLogin($0) }
                ))
                LabeledContent("Atalho global (mostrar/ocultar)") {
                    HStack(spacing: 6) {
                        Text("Option / Alt (⌥) + Espaço")
                        if !HotKeyManager.shared.isActive {
                            Text("— indisponível").foregroundStyle(.orange)
                        }
                    }
                }
            }
        }
        .formStyle(.grouped)
        .frame(minWidth: 380, maxWidth: .infinity, minHeight: 460, maxHeight: .infinity)
    }

    // O toggle lê `SMAppService.mainApp.status` direto (fonte da verdade), então
    // basta tentar registrar/desregistrar; se falhar, o toggle reflete o estado real.
    private func setLaunchAtLogin(_ on: Bool) {
        do {
            if on {
                try SMAppService.mainApp.register()
            } else {
                try SMAppService.mainApp.unregister()
            }
        } catch {
            NSLog("FronTasks: erro ao configurar início no login — \(error)")
        }
    }
}
