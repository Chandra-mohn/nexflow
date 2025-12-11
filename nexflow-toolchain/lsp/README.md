# Nexflow Language Server

Language Server Protocol (LSP) implementation for Nexflow DSLs, providing IDE support for VS Code.

## Architecture

```
lsp/
├── server/                    # Python LSP Server (pygls)
│   ├── __main__.py           # Entry point
│   ├── driver.py             # Main LSP server
│   ├── registry.py           # Module registration
│   ├── modules/
│   │   ├── base.py           # Module interface
│   │   └── proc_module.py    # L1 ProcDSL module
│   └── providers/            # Shared providers
│
└── client/                    # VS Code Extension (TypeScript)
    ├── src/
    │   └── extension.ts      # Extension entry point
    ├── syntaxes/
    │   └── procdsl.tmLanguage.json
    └── package.json
```

## Supported DSLs

| DSL | Extension | Status |
|-----|-----------|--------|
| L1 ProcDSL (Process Orchestration) | `.proc` | ✅ Implemented |
| L2 SchemaDSL (Data Schemas) | `.schema` | 🔜 Planned |
| L3 TransformDSL (Transformations) | `.xform` | 🔜 Planned |
| L4 RulesDSL (Decision Logic) | `.rules` | 🔜 Planned |

## Features

### L1 ProcDSL

- **Diagnostics**: Real-time parse error reporting
- **Completion**: Context-aware keyword suggestions
- **Hover**: Documentation on keyword hover
- **Document Symbols**: Outline view with process definitions

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- VS Code 1.75+

### Server Setup

```bash
# Install server dependencies
cd lsp/server
pip install -r requirements.txt
```

### Extension Setup

```bash
# Install extension dependencies
cd lsp/client
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package
```

## Development

### Running the Server Standalone

```bash
# stdio mode (for VS Code)
python -m lsp.server

# TCP mode (for testing)
python -m lsp.server --tcp --port 2087
```

### Testing the Extension

1. Open VS Code in the `lsp/client` directory
2. Press F5 to launch Extension Development Host
3. Open a `.proc` file to test

## Adding a New Language Module

1. Create a new module in `server/modules/`:

```python
from .base import LanguageModule, ModuleCapabilities

class MyModule(LanguageModule):
    @property
    def language_id(self) -> str:
        return "mydsl"

    @property
    def file_extensions(self) -> List[str]:
        return [".mydsl"]

    @property
    def display_name(self) -> str:
        return "MyDSL"

    def get_diagnostics(self, uri: str, content: str) -> List[Diagnostic]:
        # Implement parsing and validation
        pass
```

2. Register in `__main__.py`:

```python
from lsp.server.modules.my_module import MyModule
server.register_module(MyModule())
```

3. Add VS Code language contribution in `client/package.json`

4. Create TextMate grammar in `client/syntaxes/`

## Module Interface

Each language module implements the `LanguageModule` abstract class:

| Method | Required | Description |
|--------|----------|-------------|
| `language_id` | ✓ | Unique identifier |
| `file_extensions` | ✓ | File extensions handled |
| `display_name` | ✓ | Human-readable name |
| `get_diagnostics()` | ✓ | Parse and validate |
| `get_completions()` | | Auto-complete |
| `get_hover()` | | Hover documentation |
| `get_symbols()` | | Document outline |
| `get_definition()` | | Go to definition |
| `get_references()` | | Find references |
| `format_document()` | | Code formatting |

## Performance

- **Startup**: ~600-1000ms (Python interpreter + module loading)
- **Per-keystroke**: ~10-50ms (imperceptible)
- **Memory**: ~50-100MB (parser + AST cache)

The Python implementation trades slightly slower startup for:
- Parser code reuse (ANTLR Python runtime)
- Single codebase for backend + LSP
- Easier maintenance and development
