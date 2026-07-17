// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "Frontasks",
    platforms: [
        .macOS("15")
    ],
    targets: [
        .executableTarget(
            name: "Frontasks",
            path: "Sources/Frontasks"
        )
    ]
)
