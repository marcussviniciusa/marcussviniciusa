// Recorta a pessoa da foto com o Vision do macOS e grava a máscara (branco = pessoa).
// Uso: swift recorte.swift <foto> <mascara.png>
import CoreImage
import Foundation
import Vision

let args = CommandLine.arguments
let entrada = URL(fileURLWithPath: args[1])
let saida = URL(fileURLWithPath: args[2])

guard let foto = CIImage(contentsOf: entrada) else {
    fputs("não consegui abrir a foto\n", stderr)
    exit(1)
}

let pedido = VNGeneratePersonSegmentationRequest()
pedido.qualityLevel = .accurate
pedido.outputPixelFormat = kCVPixelFormatType_OneComponent8

try VNImageRequestHandler(ciImage: foto, options: [:]).perform([pedido])
guard let resultado = pedido.results?.first else {
    fputs("nenhuma pessoa encontrada\n", stderr)
    exit(2)
}

var mascara = CIImage(cvPixelBuffer: resultado.pixelBuffer)
mascara = mascara.transformed(by: CGAffineTransform(
    scaleX: foto.extent.width / mascara.extent.width,
    y: foto.extent.height / mascara.extent.height))

try CIContext().writePNGRepresentation(
    of: mascara, to: saida, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray())
print("máscara: \(Int(foto.extent.width))x\(Int(foto.extent.height))")
