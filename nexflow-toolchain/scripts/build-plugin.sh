#!/bin/bash
# Build VS Code plugin
# Usage: ./scripts/build-plugin.sh [--bundled]
set -e
cd "$(dirname "$0")/.."

echo "==> Installing dependencies"
cd plugin && npm install
cd webview && npm install && npm run build && cd ..

echo "==> Compiling TypeScript"
npm run compile

# Copy bundled executable if requested
if [ "$1" = "--bundled" ]; then
    echo "==> Copying nexflow executable"
    mkdir -p bin
    cp -r ../dist/nexflow/* bin/ 2>/dev/null || { echo "Error: dist/nexflow/ not found. Run build-exe.sh first."; exit 1; }
fi

echo "==> Packaging extension"
npx vsce package

# Cleanup bundled binary
[ -d bin ] && rm -rf bin

echo "==> Done: $(ls -1 *.vsix | tail -1)"
