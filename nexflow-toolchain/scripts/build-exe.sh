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

# Build with PyInstaller
$PYTHON -m PyInstaller nexflow_entry.py \
    --onefile \
    --name nexflow \
    --distpath dist/bin \
    --workpath build \
    --specpath . \
    --console \
    --collect-submodules backend \
    --collect-submodules pygls \
    --collect-submodules antlr4 \
    --hidden-import click \
    --hidden-import rich \
    --hidden-import toml \
    --log-level WARN

# Cleanup
rm -f nexflow_entry.py nexflow.spec
rm -rf build

echo "==> Done: dist/bin/nexflow"
dist/bin/nexflow --version
