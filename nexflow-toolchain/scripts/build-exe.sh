#!/bin/bash
# Build standalone nexflow executable using PyInstaller
# Usage: ./scripts/build-exe.sh
set -e
cd "$(dirname "$0")/.."

# Cross-platform Python detection (python on Windows, python3 on Mac/Linux)
if command -v python &> /dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON=python
elif command -v python3 &> /dev/null; then
    PYTHON=python3
else
    echo "Error: Python 3 not found"; exit 1
fi

echo "==> Building nexflow executable (using $PYTHON)"

# Create entry point
cat > nexflow_entry.py << 'EOF'
from backend.cli.main import cli
if __name__ == '__main__':
    cli()
EOF

# Build with PyInstaller (onedir for faster startup)
# Note: lsprotocol is required by pygls for LSP type definitions
# Exclude large unnecessary libraries to reduce bundle size
$PYTHON -m PyInstaller nexflow_entry.py \
    --onedir \
    --noconfirm \
    --name nexflow \
    --distpath dist/bin \
    --workpath build \
    --specpath . \
    --console \
    --collect-submodules backend \
    --collect-submodules pygls \
    --collect-submodules lsprotocol \
    --collect-submodules antlr4 \
    --hidden-import click \
    --hidden-import rich \
    --hidden-import toml \
    --hidden-import cattrs \
    --hidden-import attrs \
    --exclude-module numpy \
    --exclude-module scipy \
    --exclude-module pandas \
    --exclude-module matplotlib \
    --exclude-module PIL \
    --exclude-module tkinter \
    --exclude-module _tkinter \
    --exclude-module tcl \
    --exclude-module tk \
    --exclude-module IPython \
    --exclude-module jupyter \
    --exclude-module notebook \
    --exclude-module pytest \
    --exclude-module setuptools \
    --exclude-module pip \
    --log-level ERROR

# Cleanup
rm -f nexflow_entry.py nexflow.spec
rm -rf build

echo "==> Done: dist/bin/nexflow/"
dist/bin/nexflow/nexflow --version
