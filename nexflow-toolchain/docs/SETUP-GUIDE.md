#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow Setup Guide

Complete installation and configuration guide for the Nexflow toolchain and VS Code extension.

---

## Overview

Nexflow can be installed and used in multiple ways depending on your needs:

| Audience | Recommended Setup | Runtime Mode |
|----------|-------------------|--------------|
| **End Users** | VS Code extension (bundled) | Bundled executable |
| **Developers** | VS Code extension + Python source | Python mode |
| **CI/CD Pipelines** | Standalone executable | Command line |
| **Windows Users** | Pre-built `nexflow.exe` | Bundled executable |

---

## Quick Install (End Users)

### Option 1: Bundled VS Code Extension

The simplest installation - no Python required.

```bash
# Install the extension
code --install-extension nexflow-0.2.0.vsix
```

**What you get:**
- Syntax highlighting for `.proc`, `.schema`, `.xform`, `.rules` files
- Real-time error diagnostics
- Visual flow designer for `.proc` files
- Build and validate commands
- Code completion and hover documentation

**Note:** The bundled version includes `nexflow.exe` (Windows) or `nexflow` (Mac/Linux) inside the extension.

### Option 2: Standalone Executable + Basic Extension

If you prefer to install the executable separately:

1. **Download or build the executable:**
   ```bash
   # On Mac/Linux
   ./scripts/build-exe.sh
   # Output: dist/nexflow/nexflow

   # On Windows
   scripts\build-exe.sh
   # Output: dist\nexflow\nexflow.exe
   ```

2. **Add to PATH:**
   ```bash
   # Mac/Linux - add to ~/.bashrc or ~/.zshrc
   export PATH="$PATH:/path/to/dist/nexflow"

   # Windows - add to System Environment Variables
   # Settings → System → About → Advanced system settings → Environment Variables
   # Add: C:\path\to\dist\nexflow
   ```

3. **Install basic VS Code extension:**
   ```bash
   code --install-extension nexflow-0.2.0.vsix
   ```

4. **Verify installation:**
   ```bash
   nexflow --version
   # Output: nexflow, version 0.1.0
   ```

---

## Developer Setup (Full Source)

For contributors and developers who want full flexibility.

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for VS Code extension development)
- **pip** package manager

### Step 1: Clone Repository

```bash
git clone https://github.com/nexflow/nexflow-toolchain.git
cd nexflow-toolchain
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install click rich toml antlr4-python3-runtime pygls lsprotocol
```

### Step 3: Verify CLI Works

```bash
python -m backend.cli.main --version
python -m backend.cli.main --help
```

### Step 4: Install VS Code Extension (Development Mode)

```bash
cd plugin
npm install
cd webview && npm install && npm run build && cd ..
npm run compile
```

Then in VS Code:
1. Open the `plugin/` folder
2. Press `F5` to launch Extension Development Host
3. Open any `.proc` file to test

### Step 5: Configure VS Code Settings

For Python mode, the extension auto-detects the toolchain when you open the project folder. For explicit configuration:

```json
{
    "nexflow.toolchainPath": "/path/to/nexflow-toolchain",
    "nexflow.pythonPath": "/path/to/python"
}
```

---

## Runtime Modes Explained

The VS Code extension operates in one of three modes:

### 1. Bundled Mode (Recommended for End Users)

Uses the pre-built `nexflow` executable bundled inside the extension.

**How it works:**
- Extension looks for `nexflow` or `nexflow.exe` in its `bin/` folder
- Falls back to checking system PATH
- Single executable, no Python required

**Configuration:**
```json
{
    "nexflow.runtime.executable": "/custom/path/to/nexflow"
}
```

### 2. Python Mode (For Developers)

Uses Python interpreter with the source code.

**How it works:**
- Extension locates `backend/lsp/` in the project
- Runs `python -m backend.lsp` for language server
- Runs `python -m backend.cli.main` for CLI commands

**Detection order:**
1. Extension parent directory (development mode)
2. Workspace folder
3. Parent of workspace folder
4. `nexflow.toolchainPath` setting

**Configuration:**
```json
{
    "nexflow.toolchainPath": "/path/to/nexflow-toolchain",
    "nexflow.pythonPath": "/path/to/venv/bin/python",
    "nexflow.runtime.usePython": true
}
```

### 3. Visual Designer Only Mode

When no runtime is found, the extension still provides:
- Syntax highlighting
- Visual flow designer for `.proc` files
- Basic editing features

Build and validate commands will show a warning.

---

## Extension Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `nexflow.runtime.executable` | string | "" | Path to nexflow executable. Auto-detected if empty. |
| `nexflow.runtime.usePython` | boolean | false | Force Python mode instead of bundled executable. |
| `nexflow.runtime.developerMode` | boolean | false | Enable verbose error output and debug flags. |
| `nexflow.toolchainPath` | string | "" | Path to nexflow-toolchain directory. Auto-detected if empty. |
| `nexflow.pythonPath` | string | "" | Path to Python interpreter. Auto-detected if empty. |
| `nexflow.server.path` | string | "" | Deprecated. Use `nexflow.pythonPath` instead. |
| `nexflow.trace.server` | string | "off" | Trace level: "off", "messages", "verbose". |
| `nexflow.diagnostics.enabled` | boolean | true | Enable real-time diagnostics. |
| `nexflow.build.outputDirectory` | string | "src/main/java/com/nexflow/generated" | Output directory for generated Java code. |
| `nexflow.build.packageName` | string | "com.nexflow.generated" | Java package name for generated code. |

---

## Building the Extension

### Standard Build (Python Mode)

Creates extension that requires Python:

```bash
cd nexflow-toolchain
./scripts/build-plugin.sh

# Output: plugin/nexflow-0.2.0.vsix
```

### Bundled Build (No Python Required)

Creates self-contained extension with executable:

```bash
cd nexflow-toolchain

# Step 1: Build the executable
./scripts/build-exe.sh
# Output: dist/nexflow/nexflow (or nexflow.exe on Windows)

# Step 2: Build extension with bundled executable
./scripts/build-plugin.sh --bundled
# Output: plugin/nexflow-0.2.0.vsix (includes bin/nexflow)
```

### Cross-Platform Notes

| Platform | Python Command | Executable |
|----------|----------------|------------|
| Mac/Linux | `python3` | `nexflow` |
| Windows | `python` | `nexflow.exe` |

The build scripts handle cross-platform differences automatically.

---

## Troubleshooting

### "No runtime found" Message

**Cause:** Extension cannot find nexflow executable or Python source.

**Solutions:**
1. **For end users:** Install bundled VSIX or add `nexflow` to PATH
2. **For developers:** Open VS Code at project root (`nexflow-toolchain/`), not a subfolder
3. **Manual config:** Set `nexflow.runtime.executable` or `nexflow.toolchainPath`

### LSP Server Not Starting

**Check Output panel** (View → Output → "Nexflow"):
- Look for error messages
- Verify Python path is correct
- Ensure all dependencies are installed

**Python mode troubleshooting:**
```bash
# Verify Python works
python --version

# Verify dependencies
pip show pygls lsprotocol antlr4-python3-runtime

# Test LSP manually
cd nexflow-toolchain
python -m backend.lsp
```

### Extension Not Activating

1. Verify file has correct extension (`.proc`, `.schema`, `.xform`, `.rules`)
2. Check VS Code version is 1.75.0+
3. Reload window: `Ctrl+Shift+P` → "Reload Window"

### Slow Startup (Windows)

If using `--onefile` PyInstaller build, startup is slow (~10 seconds) due to extraction. Use `--onedir` build (default) for faster startup.

---

## Verifying Installation

### Check Extension Status

1. Open a `.proc` file
2. Look at status bar - should show "Nexflow"
3. Check Output panel → "Nexflow" for mode:
   - `Runtime mode: bundled` - using executable
   - `Runtime mode: python` - using Python source
   - `Runtime mode: none` - Visual Designer only

### Test CLI

```bash
# Version check
nexflow --version

# Parse a file
nexflow parse examples/building-blocks/level-1-unit/l1-procdsl/01-minimal-process.proc

# Initialize new project
nexflow init --name test-project
```

### Test Visual Designer

1. Open any `.proc` file
2. Click the graph icon in editor title bar
3. Or use Command Palette: "Nexflow: Open Visual Designer"

---

## Uninstalling

### VS Code Extension

```bash
code --uninstall-extension nexflow.nexflow
```

Or via VS Code Extensions panel → Nexflow → Uninstall

### Standalone Executable

Remove from PATH and delete the `dist/nexflow/` directory.

---

## Next Steps

| Topic | Document |
|-------|----------|
| Quick start tutorial | [QUICKSTART.md](QUICKSTART.md) |
| VS Code features | [VSCODE-EXTENSION-GUIDE.md](VSCODE-EXTENSION-GUIDE.md) |
| CLI reference | [BACKEND-USAGE.md](BACKEND-USAGE.md) |
| Windows deployment | [WINDOWS-DEPLOYMENT.md](WINDOWS-DEPLOYMENT.md) |
