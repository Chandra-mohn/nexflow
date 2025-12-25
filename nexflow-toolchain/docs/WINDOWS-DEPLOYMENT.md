# Nexflow Windows Deployment Guide

## Overview

Nexflow supports two distribution methods on Windows:

| Distribution | Audience | Use Case |
|-------------|----------|----------|
| `nexflow.exe` | End Users | Production workflows, CI/CD, no Python required |
| `python -m nexflow` | Developers | Debugging, plugin development, grammar contributions |

Both distributions have **full feature parity** - all commands work identically.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Shared Codebase                             │
│  backend/cli/main.py  ←  Single source of truth                 │
└─────────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐        ┌─────────────────────────────────┐
│   nexflow.exe       │        │   python -m nexflow             │
│   (PyInstaller)     │        │   (Editable install)            │
├─────────────────────┤        ├─────────────────────────────────┤
│ • Zero dependencies │        │ • Full Python environment       │
│ • Fast startup      │        │ • Debugger attachment (--pdb)   │
│ • Windows installer │        │ • Plugin hot-reload             │
│ • Signed binary     │        │ • Grammar development           │
└─────────────────────┘        └─────────────────────────────────┘
           │                              │
           └──────────┬───────────────────┘
                      ▼
            ┌─────────────────┐
            │  nexflow.toml   │  ← Shared configuration
            │  ~/.nexflow/    │  ← Shared user data
            └─────────────────┘
```

---

## Installation

### Option 1: Standalone Executable (Recommended for Users)

**Windows Installer (.msi)**
```powershell
# Download from GitHub Releases
Invoke-WebRequest -Uri "https://github.com/nexflow/nexflow-toolchain/releases/latest/download/nexflow-win64.msi" -OutFile nexflow.msi
Start-Process msiexec.exe -ArgumentList "/i nexflow.msi /quiet" -Wait
```

**Portable Executable**
```powershell
# Download and add to PATH
Invoke-WebRequest -Uri "https://github.com/nexflow/nexflow-toolchain/releases/latest/download/nexflow.exe" -OutFile "$env:LOCALAPPDATA\nexflow\nexflow.exe"
$env:PATH += ";$env:LOCALAPPDATA\nexflow"
```

**Chocolatey**
```powershell
choco install nexflow
```

### Option 2: Python Package (Recommended for Developers)

```powershell
# Install from PyPI
pip install nexflow

# Or for development (editable install)
git clone https://github.com/nexflow/nexflow-toolchain.git
cd nexflow-toolchain
pip install -e .
```

---

## Usage Comparison

### Parsing a DSL File

```powershell
# Using executable
nexflow.exe parse myflow.proc

# Using Python module
python -m nexflow parse myflow.proc
```

### Building a Project

```powershell
# Using executable
nexflow.exe build --target flink

# Using Python module
python -m nexflow build --target flink
```

### Developer Debugging (Python only)

```powershell
# Attach debugger on error
python -m nexflow parse myflow.proc --pdb

# Verbose output with stack traces
python -m nexflow parse myflow.proc --debug --verbose

# Profile performance
python -m nexflow build --profile
```

---

## VS Code Extension Integration

The VS Code extension automatically detects which runtime to use:

### Detection Priority

1. **User Setting**: `nexflow.runtime.executable` (if set)
2. **PATH Detection**: `nexflow.exe` in system PATH
3. **Python Fallback**: `python -m nexflow` using `nexflow.pythonPath`

### Configuration Options

Add to your VS Code settings (`settings.json`):

```json
{
  // Option A: Use standalone executable (recommended for users)
  "nexflow.runtime.executable": "C:\\Program Files\\Nexflow\\nexflow.exe",

  // Option B: Use Python module (recommended for developers)
  "nexflow.runtime.usePython": true,
  "nexflow.pythonPath": "python",

  // Developer mode: enable debug flags
  "nexflow.runtime.developerMode": true
}
```

### Setting Details

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `nexflow.runtime.executable` | string | `""` | Path to `nexflow.exe`. If empty, auto-detect from PATH. |
| `nexflow.runtime.usePython` | boolean | `false` | Force use of Python module instead of executable. |
| `nexflow.pythonPath` | string | `"python"` | Python interpreter for LSP server and Python runtime. |
| `nexflow.runtime.developerMode` | boolean | `false` | Enable debug flags (`--debug`, `--verbose`). |

### How the Extension Invokes Commands

**Current behavior** (Python only):
```typescript
spawn(pythonPath, ["-m", "backend.cli.main", "parse", filePath])
```

**New behavior** (dual runtime):
```typescript
if (useExecutable && executablePath) {
  spawn(executablePath, ["parse", filePath])
} else {
  spawn(pythonPath, ["-m", "nexflow", "parse", filePath])
}
```

---

## Building the Executable

### Prerequisites

```powershell
pip install pyinstaller
pip install -e .  # Install nexflow in editable mode
```

### Build Command

```powershell
cd nexflow-toolchain
python scripts/build_exe.py
```

### PyInstaller Spec Configuration

```python
# scripts/nexflow.spec
a = Analysis(
    ['nexflow/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('grammar/*.g4', 'grammar'),          # Error message context
        ('config/defaults.toml', 'config'),   # Default configuration
    ],
    hiddenimports=[
        'backend.parser.generated.proc',
        'backend.parser.generated.schema',
        'backend.parser.generated.transform',
        'backend.parser.generated.rules',
        'backend.generators.proc',
        'backend.generators.schema',
        'antlr4',
        'antlr4.error',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nexflow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='icons/nexflow.ico',
)
```

### Output

```
dist/
├── nexflow.exe           # Standalone executable (~25-40 MB)
└── nexflow-win64.msi     # Windows installer (generated by WiX)
```

---

## Plugin System

Plugins are **only supported in Python mode**. This is by design:

- Executable users want simplicity and reliability
- Plugin developers need the full Python environment anyway

### Plugin Discovery (Python mode only)

```python
# nexflow/plugins.py
def load_plugins():
    if is_frozen():
        return []  # No plugins in exe mode

    # Discover from entry points
    plugins = []
    for ep in pkg_resources.iter_entry_points('nexflow.plugins'):
        plugins.append(ep.load())
    return plugins
```

### Creating a Plugin

```python
# my_nexflow_plugin/plugin.py
from nexflow.plugins import NexflowPlugin

class MyPlugin(NexflowPlugin):
    name = "my-plugin"

    def register_commands(self, cli):
        @cli.command()
        def my_command():
            """My custom command."""
            pass
```

```toml
# pyproject.toml
[project.entry-points."nexflow.plugins"]
my-plugin = "my_nexflow_plugin.plugin:MyPlugin"
```

---

## Runtime Detection API

The codebase uses a unified detection mechanism:

```python
# nexflow/runtime.py
import sys

def is_frozen() -> bool:
    """True if running as PyInstaller exe."""
    return getattr(sys, 'frozen', False)

def get_runtime_mode() -> str:
    """Get current runtime mode."""
    return "exe" if is_frozen() else "python"

def get_version() -> str:
    """Get version from shared source."""
    from nexflow import __version__
    return __version__
```

---

## Error Output Differences

**Executable mode** (user-friendly):
```
✗ Parse failed: Invalid syntax at line 15
  Unexpected token 'foo', expected 'process' or 'schema'
```

**Python mode with --debug** (developer-friendly):
```
✗ Parse failed: Invalid syntax at line 15
  Unexpected token 'foo', expected 'process' or 'schema'

  File: backend/parser/proc/processing_visitor.py:234

  Traceback (most recent call last):
    File "backend/parser/proc/processing_visitor.py", line 234, in visitProcessDecl
      return self.visit(ctx.processBody())
    ...
  antlr4.error.Errors.ParseCancellationException: line 15:0 mismatched input
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      # Build executable
      - name: Build nexflow.exe
        run: |
          pip install pyinstaller
          pip install -e .
          python scripts/build_exe.py

      # Test executable
      - name: Test executable
        run: |
          dist/nexflow.exe --version
          dist/nexflow.exe parse examples/simple.proc

      # Upload artifact
      - name: Upload executable
        uses: actions/upload-artifact@v4
        with:
          name: nexflow-windows
          path: dist/nexflow.exe
```

---

## Troubleshooting

### "nexflow.exe" is not recognized

1. Check if installed: `where nexflow.exe`
2. Add to PATH: `$env:PATH += ";C:\Program Files\Nexflow"`
3. Restart terminal

### Python module not found

```powershell
pip install nexflow
# or for development
pip install -e .
```

### VS Code not detecting runtime

1. Open VS Code settings
2. Search for "nexflow"
3. Set `nexflow.runtime.executable` or `nexflow.pythonPath`
4. Reload VS Code window

### Executable crashes on startup

Try running with verbose output:
```powershell
nexflow.exe --debug parse myfile.proc
```

If issue persists, use Python mode for debugging:
```powershell
python -m nexflow --debug --pdb parse myfile.proc
```

---

## Version Synchronization

Both distributions share a single version source:

```python
# nexflow/__version__.py
__version__ = "0.8.0"
__build__ = "20241225"
```

The build process embeds this in the executable, ensuring version parity.
