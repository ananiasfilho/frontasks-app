// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "FronTasks",
    platforms: [
        .macOS("15")
    ],
    targets: [
        .executableTarget(
            name: "FronTasks",
            path: "Sources/FronTasks"
        )
    ]
)
