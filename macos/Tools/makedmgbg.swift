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

// Desenha o fundo da janela do instalador (.dmg): título + seta "arraste".
// O Finder mostra o fundo em 1 pixel = 1 ponto, então a imagem tem o tamanho
// EXATO da janela (640×400) e as coordenadas casam com a posição dos ícones.
// Coordenadas verticais aqui são medidas a partir do TOPO (como o Finder).
// Uso: swift Tools/makedmgbg.swift <saida.png>

let outPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "dmg-bg.png"
let W: CGFloat = 640, H: CGFloat = 400

guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil, pixelsWide: Int(W), pixelsHigh: Int(H),
    bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
    colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0
) else { fatalError("rep") }
rep.size = NSSize(width: W, height: H)

NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

// y a partir do topo -> y do AppKit (origem embaixo).
func top(_ y: CGFloat) -> CGFloat { H - y }

// Fundo em gradiente suave.
if let g = NSGradient(
    starting: NSColor(srgbRed: 0.97, green: 0.98, blue: 1.00, alpha: 1),
    ending:   NSColor(srgbRed: 0.89, green: 0.92, blue: 0.97, alpha: 1)
) {
    g.draw(in: NSRect(x: 0, y: 0, width: W, height: H), angle: -90)
}

// Seta azul entre o app (x≈170) e a pasta Applications (x≈470), no meio (y≈205).
let blue = NSColor(srgbRed: 0.23, green: 0.51, blue: 0.96, alpha: 0.95)
blue.setStroke()
let ay = top(205)
let shaft = NSBezierPath()
shaft.lineWidth = 8
shaft.lineCapStyle = .round
shaft.move(to: NSPoint(x: 262, y: ay))
shaft.line(to: NSPoint(x: 372, y: ay))
shaft.stroke()
let head = NSBezierPath()
head.lineWidth = 8
head.lineJoinStyle = .round
head.lineCapStyle = .round
head.move(to: NSPoint(x: 364, y: ay + 18))
head.line(to: NSPoint(x: 396, y: ay))
head.line(to: NSPoint(x: 364, y: ay - 18))
head.stroke()

// Textos centralizados.
func drawCentered(_ s: String, size: CGFloat, weight: NSFont.Weight, color: NSColor, topY: CGFloat) {
    let ps = NSMutableParagraphStyle(); ps.alignment = .center
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: size, weight: weight),
        .foregroundColor: color,
        .paragraphStyle: ps
    ]
    let str = NSAttributedString(string: s, attributes: attrs)
    let h = str.size().height
    str.draw(in: NSRect(x: 0, y: top(topY) - h, width: W, height: h))
}

drawCentered("Frontasks", size: 34, weight: .bold,
             color: NSColor(srgbRed: 0.11, green: 0.15, blue: 0.22, alpha: 1), topY: 48)
drawCentered("Arraste o ícone para a pasta Applications", size: 15, weight: .regular,
             color: NSColor(srgbRed: 0.34, green: 0.40, blue: 0.47, alpha: 1), topY: 92)

NSGraphicsContext.restoreGraphicsState()

guard let data = rep.representation(using: .png, properties: [:]) else { fatalError("png") }
try! data.write(to: URL(fileURLWithPath: outPath))
print("bg -> \(outPath)")
