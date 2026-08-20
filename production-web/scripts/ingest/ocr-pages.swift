import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count >= 2 else {
    fputs("Uso: swift ocr-pages.swift <imagen> [imagen...]\n", stderr)
    exit(2)
}

for imagePath in CommandLine.arguments.dropFirst() {
    guard let image = NSImage(contentsOfFile: imagePath),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fputs("No se pudo abrir: \(imagePath)\n", stderr)
        continue
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["es-ES", "en-US"]
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: cgImage).perform([request])

    let observations = (request.results ?? []).sorted {
        if abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.008 {
            return $0.boundingBox.midY > $1.boundingBox.midY
        }
        return $0.boundingBox.minX < $1.boundingBox.minX
    }
    for observation in observations {
        guard let candidate = observation.topCandidates(1).first else { continue }
        let box = observation.boundingBox
        let safeText = candidate.string.replacingOccurrences(of: "\t", with: " ")
        print("\(URL(fileURLWithPath: imagePath).lastPathComponent)\t\(box.minX)\t\(box.minY)\t\(box.width)\t\(box.height)\t\(safeText)")
    }
}
