# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
- Python 3.11+ with pip
- Required Python packages: `pygls`, `lsprotocol`

### From VSIX Package
```bash
# Install the extension from package
code --install-extension nexflow-lsp-0.1.0.vsix
```

### From Source (Development)
```bash
# Navigate to client directory
cd lsp/client

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# For development with auto-rebuild
npm run watch
```

### Python Server Dependencies
```bash
# Install Python LSP dependencies
pip install pygls lsprotocol
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
| ProcDSL | `process`, `receive`, `emit`, `transform`, `route`, `persist`, `state`, `each`, `parallel`, `branch` |
| SchemaDSL | `schema`, `entity`, `field`, `required`, `optional`, `constraint`, `pattern` |
| TransformDSL | `transform`, `input`, `output`, `mapping`, `field`, `filter`, `flatten` |
| RulesDSL | `rules`, `decision`, `when`, `then`, `otherwise`, `hit_policy` |

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
| `nexflow.server.path` | Path to Python interpreter for LSP server | System Python |
| `nexflow.trace.server` | Trace level: `off`, `messages`, `verbose` | `off` |
| `nexflow.diagnostics.enabled` | Enable real-time diagnostics | `true` |

### Example settings.json
```json
{
    "nexflow.server.path": "/path/to/venv/bin/python",
    "nexflow.trace.server": "messages",
    "nexflow.diagnostics.enabled": true
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
├── flows/           # L1 process definitions
│   ├── main.proc
│   └── handlers/
├── schemas/         # L2 schema definitions
│   ├── input.schema
│   └── output.schema
├── transforms/      # L3 transformations
│   └── mappings.xform
├── rules/           # L4 business rules
│   └── validation.rules
└── infra/           # L5 infrastructure bindings
    └── config.infra
```

### Imports
Nexflow DSLs support importing definitions from other files:

```
// In a .proc file
import "schemas/input.schema"
import "transforms/mappings.xform"
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

## Troubleshooting

### Extension Not Activating
1. Ensure file has correct extension (`.proc`, `.schema`, `.xform`, `.rules`)
2. Check VS Code version is 1.75.0+
3. Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")

### LSP Server Not Starting
1. Check Python is installed and accessible
2. Verify required packages: `pip show pygls lsprotocol`
3. Check Output panel ("Nexflow LSP") for error messages
4. Try setting explicit Python path in settings

### No Diagnostics Appearing
1. Ensure `nexflow.diagnostics.enabled` is `true`
2. Check file is saved (some diagnostics require save)
3. Look for errors in Output panel

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
│   - UI          │        │   │ ProcModule│ │
│   - File Watch  │        │   │ SchemaModule│
│   - Triggers    │        │   │ TransformModule│
│                 │        │   │ RulesModule │
└─────────────────┘        └───┴───────────┘─┘
```

### Language Modules
Each DSL has a dedicated Python module:
- `ProcModule` - L1 ProcDSL parsing and validation
- `SchemaModule` - L2 SchemaDSL parsing and validation
- `TransformModule` - L3 TransformDSL parsing and validation
- `RulesModule` - L4 RulesDSL parsing and validation

Modules implement the `LanguageModule` interface providing:
- `get_diagnostics()` - Parse errors and warnings
- `get_completions()` - Auto-completion items
- `get_hover()` - Hover documentation
- `get_symbols()` - Document outline
- `get_definition()` - Go to definition
- `get_references()` - Find all references
- `format_document()` - Code formatting

## Development

### Building the Extension
```bash
cd lsp/client
npm run compile
npm run package  # Creates .vsix file
```

### Running Tests
```bash
npm run test
```

### Development Mode
1. Open `lsp/client` in VS Code
2. Press `F5` to launch Extension Development Host
3. Open a `.proc` file to test

### Modifying Server
The Python server is in `lsp/server/`:
- `driver.py` - Main LSP server
- `registry.py` - Module registry
- `modules/` - Language-specific modules
- `__main__.py` - Entry point

## Version History

### 0.1.0
- Initial release
- Support for all four DSL languages
- Real-time diagnostics
- Syntax highlighting
- Basic code completion
- Document outline
