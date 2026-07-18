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

import AppKit

// Renderiza a arte do ícone (1024×1024) seguindo a grade de ícones da Apple:
// squircle ~824px centrado, gradiente azul, glifo "checklist" branco.

let size = 1024
guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: size, pixelsHigh: size,
    bitsPerSample: 8, samplesPerPixel: 4,
    hasAlpha: true, isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: 0, bitsPerPixel: 0
) else { fatalError("rep") }
rep.size = NSSize(width: size, height: size)

NSGraphicsContext.saveGraphicsState()
guard let ctx = NSGraphicsContext(bitmapImageRep: rep) else { fatalError("ctx") }
NSGraphicsContext.current = ctx

// Fundo transparente.
NSColor.clear.set()
NSRect(x: 0, y: 0, width: size, height: size).fill()

// Squircle com gradiente — azul em full-bleed (sem margem, só cantos arredondados).
let inset: CGFloat = 0
let sq = NSRect(x: inset, y: inset,
                width: CGFloat(size) - 2 * inset,
                height: CGFloat(size) - 2 * inset)
let path = NSBezierPath(roundedRect: sq, xRadius: 230, yRadius: 230)

let top = NSColor(srgbRed: 0.36, green: 0.64, blue: 1.00, alpha: 1) // azul claro
let bottom = NSColor(srgbRed: 0.15, green: 0.39, blue: 0.92, alpha: 1) // azul profundo
if let grad = NSGradient(starting: top, ending: bottom) {
    ctx.saveGraphicsState()
    path.addClip()
    grad.draw(in: sq, angle: -90) // de cima para baixo

    // Brilho sutil no topo.
    if let sheen = NSGradient(colors: [
        NSColor.white.withAlphaComponent(0.18),
        NSColor.white.withAlphaComponent(0.0)
    ]) {
        sheen.draw(in: NSRect(x: sq.minX, y: sq.midY, width: sq.width, height: sq.height / 2),
                   angle: -90)
    }
    ctx.restoreGraphicsState()
}

// Glifo checklist em branco, centralizado.
let cfg = NSImage.SymbolConfiguration(pointSize: 470, weight: .semibold)
if let base = NSImage(systemSymbolName: "checklist", accessibilityDescription: nil),
   let sym = base.withSymbolConfiguration(cfg) {
    let symSize = sym.size
    let tinted = NSImage(size: symSize)
    tinted.lockFocus()
    NSColor.white.set()
    let r = NSRect(origin: .zero, size: symSize)
    sym.draw(in: r)
    r.fill(using: .sourceAtop)
    tinted.unlockFocus()

    let box = NSRect(x: 252, y: 272, width: 520, height: 500)
    let scale = min(box.width / symSize.width, box.height / symSize.height)
    let w = symSize.width * scale
    let h = symSize.height * scale
    let dst = NSRect(x: box.midX - w / 2, y: box.midY - h / 2, width: w, height: h)
    tinted.draw(in: dst)
}

NSGraphicsContext.restoreGraphicsState()

guard let data = rep.representation(using: .png, properties: [:]) else { fatalError("png") }
try! data.write(to: URL(fileURLWithPath: "Icon/icon_1024.png"))
print("✓ Icon/icon_1024.png")
