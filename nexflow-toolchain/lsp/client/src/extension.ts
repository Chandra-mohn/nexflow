// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * Nexflow LSP Extension
 *
 * VS Code extension that spawns the Python language server
 * and provides language support for Nexflow DSLs.
 */

import * as path from "path";
import * as fs from "fs";
import { workspace, ExtensionContext, window, OutputChannel } from "vscode";

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let outputChannel: OutputChannel;

/**
 * Find the Python executable to use for the LSP server.
 */
function findPythonPath(): string {
  // Check user configuration first
  const config = workspace.getConfiguration("nexflow");
  const configuredPath = config.get<string>("server.path");

  if (configuredPath && fs.existsSync(configuredPath)) {
    return configuredPath;
  }

  // Check for virtual environment in workspace
  const workspaceFolders = workspace.workspaceFolders;
  if (workspaceFolders) {
    for (const folder of workspaceFolders) {
      const venvPaths = [
        path.join(folder.uri.fsPath, ".venv", "bin", "python"),
        path.join(folder.uri.fsPath, ".venv", "Scripts", "python.exe"),
        path.join(folder.uri.fsPath, "venv", "bin", "python"),
        path.join(folder.uri.fsPath, "venv", "Scripts", "python.exe"),
      ];

      for (const venvPath of venvPaths) {
        if (fs.existsSync(venvPath)) {
          return venvPath;
        }
      }
    }
  }

  // Fall back to system Python
  return process.platform === "win32" ? "python" : "python3";
}

/**
 * Find the project root (where lsp/ directory lives).
 * This is needed for PYTHONPATH so `python -m lsp.server` works.
 */
function findProjectRoot(context: ExtensionContext): string {
  // Extension is at lsp/client, so project root is lsp/client/../../ = project root
  // context.extensionPath = /path/to/nexflow-toolchain/lsp/client
  // We need: /path/to/nexflow-toolchain

  const projectRoot = path.resolve(context.extensionPath, "..", "..");

  // Verify lsp/server exists at this location
  const serverPath = path.join(projectRoot, "lsp", "server");
  if (fs.existsSync(serverPath)) {
    return projectRoot;
  }

  // Fallback: check if we're in a different structure
  // Maybe lsp/ is at the workspace root
  const workspaceFolders = workspace.workspaceFolders;
  if (workspaceFolders) {
    for (const folder of workspaceFolders) {
      const wsServerPath = path.join(folder.uri.fsPath, "lsp", "server");
      if (fs.existsSync(wsServerPath)) {
        return folder.uri.fsPath;
      }
    }
  }

  return "";
}

/**
 * Activate the extension.
 */
export async function activate(context: ExtensionContext): Promise<void> {
  outputChannel = window.createOutputChannel("Nexflow LSP");
  context.subscriptions.push(outputChannel);

  outputChannel.appendLine("Activating Nexflow LSP extension...");

  const pythonPath = findPythonPath();
  const projectRoot = findProjectRoot(context);

  outputChannel.appendLine(`Python path: ${pythonPath}`);
  outputChannel.appendLine(`Project root: ${projectRoot}`);
  outputChannel.appendLine(`Extension path: ${context.extensionPath}`);

  if (!projectRoot) {
    const errorMsg = "Could not find LSP server. Please ensure the extension is installed correctly.";
    outputChannel.appendLine(errorMsg);
    window.showErrorMessage(errorMsg);
    return;
  }

  // Server options - spawn Python process
  // We run from project root with lsp.server as module
  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: ["-m", "lsp.server"],
    options: {
      cwd: projectRoot,
      env: {
        ...process.env,
        PYTHONPATH: projectRoot,
      },
    },
  };

  outputChannel.appendLine(`Server command: ${pythonPath} -m lsp.server`);
  outputChannel.appendLine(`Server cwd: ${projectRoot}`);

  // Client options
  const clientOptions: LanguageClientOptions = {
    // Register for all Nexflow DSL file types
    documentSelector: [
      { scheme: "file", language: "procdsl" },
      { scheme: "file", language: "schemadsl" },
      { scheme: "file", language: "transformdsl" },
      { scheme: "file", language: "rulesdsl" },
      // Also match by extension pattern
      { scheme: "file", pattern: "**/*.proc" },
      { scheme: "file", pattern: "**/*.schema" },
      { scheme: "file", pattern: "**/*.xform" },
      { scheme: "file", pattern: "**/*.rules" },
    ],
    synchronize: {
      // Watch for changes to DSL files
      fileEvents: workspace.createFileSystemWatcher("**/*.{proc,schema,xform,rules}"),
    },
    outputChannel: outputChannel,
    traceOutputChannel: outputChannel,
  };

  // Create and start the language client
  client = new LanguageClient(
    "nexflowLsp",
    "Nexflow Language Server",
    serverOptions,
    clientOptions
  );

  outputChannel.appendLine("Starting Nexflow Language Server...");

  try {
    await client.start();
    outputChannel.appendLine("Nexflow Language Server started successfully");
  } catch (error) {
    outputChannel.appendLine(`Failed to start server: ${error}`);
    window.showErrorMessage(
      `Failed to start Nexflow Language Server: ${error}. ` +
      "Please ensure Python and required packages (pygls, lsprotocol) are installed."
    );
  }

  context.subscriptions.push({
    dispose: () => {
      if (client) {
        return client.stop();
      }
      return undefined;
    },
  });
}

/**
 * Deactivate the extension.
 */
export async function deactivate(): Promise<void> {
  if (client) {
    await client.stop();
  }
}
