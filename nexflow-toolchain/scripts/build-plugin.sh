#!/bin/bash
# Build VS Code plugin
# Usage: ./scripts/build-plugin.sh [--no-bundle]
#   Default: bundles nexflow executable into plugin
#   --no-bundle: skip bundling (smaller package, requires separate nexflow install)
set -e
cd "$(dirname "$0")/.."

echo "==> Installing dependencies"
cd plugin && npm install
cd webview && npm install && npm run build && cd ..

echo "==> Compiling TypeScript"
npm run compile

# Bundle executable by default, skip with --no-bundle
if [ "$1" != "--no-bundle" ]; then
    echo "==> Bundling nexflow executable"
    mkdir -p bin
    cp -r ../dist/bin/nexflow/* bin/ 2>/dev/null || { echo "Error: dist/bin/nexflow/ not found. Run build-exe.sh first."; exit 1; }
fi

echo "==> Packaging extension"
# Note: vsce runs vscode:prepublish automatically, which rebuilds webview and compiles TypeScript
# We've already done this above, but vsce expects it in prepublish for consistency
mkdir -p ../dist
npx vsce package --no-dependencies --out ../dist/

# Cleanup bundled binary
[ -d bin ] && rm -rf bin

VSIX=$(ls -1 ../dist/*.vsix | tail -1)
echo "==> Done: $VSIX"
