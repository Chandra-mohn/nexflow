#### Nexflow DSL Toolchain
#### Author: Chandra Mohn

# Nexflow VS Code Extension User Guide

## Overview

The Nexflow VS Code Extension provides comprehensive IDE support for all Nexflow DSL languages:
- **L1 ProcDSL** (`.proc`) - Process Orchestration
- **L2 SchemaDSL** (`.schema`) - Data Schema Definitions
- **L3 TransformDSL** (`.xform`, `.transform`) - Data Transformations
- **L4 RulesDSL** (`.rules`) - Business Decision Logic

## Installation

### Prerequisites
- VS Code 1.75.0 or higher
- Python 3.11+ (for Python mode) OR bundled executable

### From VSIX Package
```bash
# Install the extension
code --install-extension nexflow-0.2.0.vsix
```

### Runtime Modes

The extension supports two runtime modes:

| Mode | Description | When to Use |
|------|-------------|-------------|
| **Python** | Uses system Python + LSP server | Development, full flexibility |
| **Bundled** | Self-contained executable | Production, no Python required |

Configure in VS Code settings:
```json
{
    "nexflow.runtime.mode": "python",  // or "bundled"
    "nexflow.server.path": "/path/to/python"  // Python mode only
}
```

## Features

### Real-Time Diagnostics
The extension provides real-time syntax and semantic validation:
- Syntax errors highlighted as you type
- Semantic warnings for potential issues
- Errors displayed in Problems panel

### Syntax Highlighting
Full syntax highlighting for all DSL keywords:

| DSL | Keywords |
|-----|----------|
| ProcDSL | `process`, `receive`, `emit`, `transform`, `route`, `persist`, `state`, `parallel`, `branch`, `enrich`, `lookup` |
| SchemaDSL | `schema`, `entity`, `field`, `required`, `optional`, `constraint`, `pattern`, `serialization` |
| TransformDSL | `transform`, `input`, `output`, `mapping`, `field`, `filter`, `flatten` |
| RulesDSL | `rules`, `decision`, `when`, `then`, `otherwise`, `hit_policy` |

### Visual Flow Designer (NEW)

For `.proc` files, the extension includes an interactive visual designer:

**Opening the Designer:**
1. Open any `.proc` file
2. Click the **"Open Visual Designer"** icon in the editor title bar
3. Or use Command Palette: `Nexflow: Open Visual Designer`

**Designer Features:**
- Interactive node-based flow visualization
- Drag-and-drop node positioning
- Zoom and pan navigation
- Export flow as PNG image
- Real-time sync with code editor
- Node types: Source, Sink, Transform, Route, Enrich, Persist

**Node Color Legend:**
| Color | Node Type |
|-------|-----------|
| Blue | Source (receive) |
| Green | Sink (emit) |
| Purple | Transform |
| Orange | Route/Branch |
| Cyan | Enrich/Lookup |
| Gray | Persist |

### Code Completion
Context-aware auto-completion:
- DSL keywords at block level
- Built-in function names
- Type suggestions
- Import path completion

### Hover Documentation
Hover over keywords and identifiers to see:
- Syntax documentation
- Type information
- Parameter descriptions
- Usage examples

### Document Outline
View document structure in the Outline panel:
- Process definitions
- Schema entities
- Transform definitions
- Rule tables

### Code Folding
Fold/unfold DSL blocks:
- Process blocks
- Stage definitions
- Schema entities
- Transform mappings
- Decision tables

## Configuration

### Extension Settings

Access settings via `File > Preferences > Settings` and search for "Nexflow".

| Setting | Description | Default |
|---------|-------------|---------|
| `nexflow.runtime.mode` | Runtime mode: `python` or `bundled` | `python` |
| `nexflow.server.path` | Path to Python interpreter (Python mode) | System Python |
| `nexflow.trace.server` | Trace level: `off`, `messages`, `verbose` | `off` |
| `nexflow.diagnostics.enabled` | Enable real-time diagnostics | `true` |
| `nexflow.visualDesigner.autoOpen` | Auto-open designer for .proc files | `false` |

### Example settings.json
```json
{
    "nexflow.runtime.mode": "python",
    "nexflow.server.path": "/path/to/venv/bin/python",
    "nexflow.trace.server": "messages",
    "nexflow.diagnostics.enabled": true,
    "nexflow.visualDesigner.autoOpen": false
}
```

## File Associations

The extension automatically associates these file types:

| Extension | Language | DSL Layer |
|-----------|----------|-----------|
| `.proc` | ProcDSL | L1 |
| `.schema` | SchemaDSL | L2 |
| `.xform` | TransformDSL | L3 |
| `.transform` | TransformDSL | L3 |
| `.rules` | RulesDSL | L4 |

## Working with Nexflow Projects

### Project Structure
A typical Nexflow project has this structure:
```
my-project/
├── nexflow.toml         # Project configuration
├── src/
│   ├── flow/            # L1 process definitions
│   │   └── main.proc
│   ├── schema/          # L2 schema definitions
│   │   ├── input.schema
│   │   └── output.schema
│   ├── transform/       # L3 transformations
│   │   └── mappings.xform
│   └── rules/           # L4 business rules
│       └── validation.rules
└── generated/           # Output directory
```

### Imports
Nexflow DSLs support importing definitions from other files:

```
// In a .proc file
import "schema/input.schema"
import "transform/mappings.xform"
import "rules/validation.rules"
```

The extension validates import paths and provides go-to-definition support.

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Trigger Completion | `Ctrl+Space` | `Cmd+Space` |
| Quick Fix | `Ctrl+.` | `Cmd+.` |
| Go to Definition | `F12` | `F12` |
| Find All References | `Shift+F12` | `Shift+F12` |
| Rename Symbol | `F2` | `F2` |
| Format Document | `Shift+Alt+F` | `Shift+Option+F` |
| Toggle Outline | `Ctrl+Shift+O` | `Cmd+Shift+O` |
| Open Visual Designer | - | - |

## Troubleshooting

### Extension Not Activating
1. Ensure file has correct extension (`.proc`, `.schema`, `.xform`, `.rules`)
2. Check VS Code version is 1.75.0+
3. Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")

### LSP Server Not Starting
1. Check Python is installed and accessible (Python mode)
2. Verify required packages: `pip show pygls lsprotocol`
3. Check Output panel ("Nexflow LSP") for error messages
4. Try setting explicit Python path in settings

### No Diagnostics Appearing
1. Ensure `nexflow.diagnostics.enabled` is `true`
2. Check file is saved (some diagnostics require save)
3. Look for errors in Output panel

### Visual Designer Not Opening
1. Ensure file is a `.proc` file
2. Check for parse errors in the file first
3. Try reloading the window

### Server Crashes
1. Enable verbose tracing: set `nexflow.trace.server` to `verbose`
2. Check Output panel for stack traces
3. Ensure ANTLR4 parser files are generated

### View LSP Logs
1. Open Output panel (`Ctrl+Shift+U` / `Cmd+Shift+U`)
2. Select "Nexflow LSP" from dropdown
3. Watch for connection status and errors

## Architecture

### Client-Server Model
```
┌─────────────────┐        ┌─────────────────┐
│   VS Code       │        │   Python LSP    │
│   Extension     │◄──────►│   Server        │
│   (TypeScript)  │  JSON  │                 │
│                 │  RPC   │   ┌───────────┐ │
│   - UI/Webview  │        │   │ ProcModule│ │
│   - File Watch  │        │   │ SchemaModule│
│   - Triggers    │        │   │ TransformModule│
│                 │        │   │ RulesModule │
└─────────────────┘        └───┴───────────┘─┘
```

### Extension Components

```
plugin/
├── src/                  # TypeScript extension source
│   ├── extension.ts      # Main entry point
│   ├── lspClient.ts      # Language client
│   └── visualDesigner.ts # Webview provider
├── webview/              # React visual designer
│   └── src/
│       ├── App.tsx
│       └── components/
├── syntaxes/             # TextMate grammars
│   ├── proc.tmLanguage.json
│   ├── schema.tmLanguage.json
│   ├── transform.tmLanguage.json
│   └── rules.tmLanguage.json
└── package.json          # Extension manifest
```

### Language Server (Python)

```
backend/lsp/
├── __main__.py           # Entry point
├── driver.py             # Main LSP server
├── registry.py           # Module registry
└── modules/
    ├── proc_module.py    # L1 ProcDSL
    ├── schema_module.py  # L2 SchemaDSL
    ├── transform_module.py # L3 TransformDSL
    └── rules_module.py   # L4 RulesDSL
```

### Language Modules
Each DSL has a dedicated Python module implementing:
- `get_diagnostics()` - Parse errors and warnings
- `get_completions()` - Auto-completion items
- `get_hover()` - Hover documentation
- `get_symbols()` - Document outline
- `get_definition()` - Go to definition
- `get_references()` - Find all references
- `format_document()` - Code formatting

## Building the Extension

### Prerequisites
- Node.js 18+
- npm

### Build Scripts

```bash
# Build the VS Code plugin (Python mode)
./scripts/build-plugin.sh

# Build with bundled executable
./scripts/build-exe.sh        # First, build the executable
./scripts/build-plugin.sh --bundled  # Then, bundle it
```

### Development Mode
1. Open `plugin/` in VS Code
2. Run `npm install`
3. Press `F5` to launch Extension Development Host
4. Open a `.proc` file to test

### Manual Build
```bash
cd plugin
npm install
cd webview && npm install && npm run build && cd ..
npm run compile
npx vsce package
```

## Version History

### 0.2.0 (Current)
- Visual flow designer for `.proc` files
- Bundled executable mode (no Python required)
- Improved diagnostics and error messages
- PNG export from visual designer
- Cross-platform build scripts

### 0.1.0
- Initial release
- Support for all four DSL languages
- Real-time diagnostics
- Syntax highlighting
- Basic code completion
- Document outline
