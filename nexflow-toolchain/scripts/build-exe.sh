#!/bin/bash
# Build standalone nexflow executable using PyInstaller
# Usage: ./scripts/build-exe.sh
set -e
cd "$(dirname "$0")/.."

echo "==> Building nexflow executable"

# Create entry point
cat > nexflow_entry.py << 'EOF'
from backend.cli.main import cli
if __name__ == '__main__':
    cli()
EOF

# Build with PyInstaller
python3 -m PyInstaller nexflow_entry.py \
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
