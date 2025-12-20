// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * Nexflow Extension
 *
 * VS Code extension providing:
 * - Language Server Protocol (LSP) support for Nexflow DSLs
 * - Build commands for code generation
 * - Visual Designer for L1 Process topology
 */

import * as path from "path";
import * as fs from "fs";
import {
  workspace,
  ExtensionContext,
  window,
  OutputChannel,
  commands,
  Uri,
} from "vscode";

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
} from "vscode-languageclient/node";

import { BuildRunner } from "./buildRunner";
import { VisualDesignerPanel } from "./visualDesigner/panel";

let client: LanguageClient | undefined;
let outputChannel: OutputChannel;
let buildOutputChannel: OutputChannel;
let buildRunner: BuildRunner | undefined;

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
 * Find the project root (where lsp/ and backend/ directories live).
 * This is needed for PYTHONPATH so Python modules work.
 */
function findProjectRoot(context: ExtensionContext): string {
  // Extension is at plugin/, so project root is plugin/../ = project root
  // context.extensionPath = /path/to/nexflow-toolchain/plugin
  // We need: /path/to/nexflow-toolchain

  const projectRoot = path.resolve(context.extensionPath, "..");

  // Verify lsp/server exists at this location
  const serverPath = path.join(projectRoot, "lsp", "server");
  if (fs.existsSync(serverPath)) {
    return projectRoot;
  }

  // Also check for backend/ (for CLI commands)
  const backendPath = path.join(projectRoot, "backend");
  if (fs.existsSync(backendPath)) {
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
  // Create output channel first for logging
  outputChannel = window.createOutputChannel("Nexflow");
  context.subscriptions.push(outputChannel);
  outputChannel.show(true); // Show output for debugging

  try {
    outputChannel.appendLine("Activating Nexflow extension...");
    outputChannel.appendLine(`Extension path: ${context.extensionPath}`);

    const pythonPath = findPythonPath();
    const projectRoot = findProjectRoot(context);

    outputChannel.appendLine(`Python path: ${pythonPath}`);
    outputChannel.appendLine(`Project root: ${projectRoot || "(not found)"}`);
    outputChannel.appendLine(`Workspace folders: ${workspace.workspaceFolders?.map(f => f.uri.fsPath).join(", ") || "(none)"}`);
    outputChannel.appendLine("Registering commands...");

  // Register Visual Designer command FIRST (works without LSP server)
  const visualDesignerCommand = commands.registerCommand(
    "nexflow.openVisualDesigner",
    async (uri?: Uri) => {
      let filePath: string | undefined;

      if (uri) {
        filePath = uri.fsPath;
      } else {
        // Called from command palette - use active editor if it's a .proc file
        const activeEditor = window.activeTextEditor;
        if (activeEditor && activeEditor.document.uri.fsPath.endsWith(".proc")) {
          filePath = activeEditor.document.uri.fsPath;
        }
      }

      // Validate file extension
      if (filePath && !filePath.endsWith(".proc")) {
        window.showErrorMessage("Visual Designer only supports .proc files");
        return;
      }

      // For Visual Designer, we need a project root for CLI - use workspace folder or toolchain root
      const effectiveRoot = projectRoot || workspace.workspaceFolders?.[0]?.uri.fsPath || "";

      if (!effectiveRoot) {
        window.showErrorMessage("Please open a workspace folder first");
        return;
      }

      VisualDesignerPanel.createOrShow(
        context.extensionUri,
        effectiveRoot,
        pythonPath,
        filePath
      );
    }
  );
  context.subscriptions.push(visualDesignerCommand);

  // Register command to open Visual Designer from .proc.ui file
  const visualDesignerFromUICommand = commands.registerCommand(
    "nexflow.openVisualDesignerFromUI",
    async (uri?: Uri) => {
      let uiFilePath: string | undefined;

      if (uri) {
        uiFilePath = uri.fsPath;
      } else {
        // Called from command palette - use active editor if it's a .proc.ui file
        const activeEditor = window.activeTextEditor;
        if (activeEditor && activeEditor.document.uri.fsPath.endsWith(".proc.ui")) {
          uiFilePath = activeEditor.document.uri.fsPath;
        }
      }

      // Validate file extension
      if (!uiFilePath || !uiFilePath.endsWith(".proc.ui")) {
        window.showErrorMessage("This command only works with .proc.ui files");
        return;
      }

      // Derive .proc file path from .proc.ui path (remove .ui suffix)
      const procFilePath = uiFilePath.replace(/\.ui$/, "");

      // Check if .proc file exists
      if (!fs.existsSync(procFilePath)) {
        window.showErrorMessage(`Source file not found: ${path.basename(procFilePath)}`);
        return;
      }

      // For Visual Designer, we need a project root for CLI
      const effectiveRoot = projectRoot || workspace.workspaceFolders?.[0]?.uri.fsPath || "";

      if (!effectiveRoot) {
        window.showErrorMessage("Please open a workspace folder first");
        return;
      }

      VisualDesignerPanel.createOrShow(
        context.extensionUri,
        effectiveRoot,
        pythonPath,
        procFilePath
      );
    }
  );
  context.subscriptions.push(visualDesignerFromUICommand);
  outputChannel.appendLine("Visual Designer commands registered");

  // If no project root (LSP server not available), register placeholder commands and exit
  if (!projectRoot) {
    outputChannel.appendLine("LSP server not found - registering placeholder commands");

    // Placeholder build command
    const buildCommand = commands.registerCommand("nexflow.build", () => {
      window.showWarningMessage(
        "Nexflow build requires the toolchain. Visual Designer is available for .proc files."
      );
    });
    context.subscriptions.push(buildCommand);

    const validateCommand = commands.registerCommand("nexflow.validate", () => {
      window.showWarningMessage(
        "Nexflow validate requires the toolchain. Visual Designer is available for .proc files."
      );
    });
    context.subscriptions.push(validateCommand);

    const generateFileCommand = commands.registerCommand("nexflow.generateFile", () => {
      window.showWarningMessage(
        "Nexflow generate requires the toolchain. Visual Designer is available for .proc files."
      );
    });
    context.subscriptions.push(generateFileCommand);

    outputChannel.appendLine("Nexflow activated (Visual Designer only - LSP server not available)");
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

  // Create build output channel and runner
  buildOutputChannel = window.createOutputChannel("Nexflow Build");
  context.subscriptions.push(buildOutputChannel);

  buildRunner = new BuildRunner(buildOutputChannel, projectRoot, pythonPath);

  // Register build command
  const buildCommand = commands.registerCommand(
    "nexflow.build",
    async (uri?: Uri) => {
      if (!buildRunner) {
        window.showErrorMessage("Nexflow build runner not initialized");
        return;
      }

      let sourceDir: string;

      if (uri && fs.statSync(uri.fsPath).isDirectory()) {
        // Called from folder context menu
        sourceDir = uri.fsPath;
      } else {
        // Called from command palette or editor - use workspace root
        const workspaceFolder = workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
          window.showErrorMessage("No workspace folder open");
          return;
        }
        sourceDir = workspaceFolder.uri.fsPath;
      }

      const result = await buildRunner.buildProject(sourceDir);

      if (result.success) {
        window.showInformationMessage(
          `Nexflow build successful! Generated ${result.generatedFiles} files.`
        );
      } else {
        window.showErrorMessage(
          `Nexflow build failed with ${result.errors.length} error(s). Check Output panel for details.`
        );
      }
    }
  );
  context.subscriptions.push(buildCommand);

  // Register validate command
  const validateCommand = commands.registerCommand(
    "nexflow.validate",
    async () => {
      if (!buildRunner) {
        window.showErrorMessage("Nexflow build runner not initialized");
        return;
      }

      const workspaceFolder = workspace.workspaceFolders?.[0];
      if (!workspaceFolder) {
        window.showErrorMessage("No workspace folder open");
        return;
      }

      const result = await buildRunner.validateProject(
        workspaceFolder.uri.fsPath
      );

      if (result.success) {
        const total =
          result.schemasCount +
          result.transformsCount +
          result.processesCount +
          result.rulesCount;
        window.showInformationMessage(
          `Nexflow validation successful! ${total} definitions validated.`
        );
      } else {
        window.showErrorMessage(
          `Nexflow validation failed. Check Output panel for details.`
        );
      }
    }
  );
  context.subscriptions.push(validateCommand);

  // Register generate file command (for context menu)
  const generateFileCommand = commands.registerCommand(
    "nexflow.generateFile",
    async (uri?: Uri) => {
      if (!buildRunner) {
        window.showErrorMessage("Nexflow build runner not initialized");
        return;
      }

      let filePath: string;

      if (uri) {
        filePath = uri.fsPath;
      } else {
        // Called from command palette - use active editor
        const activeEditor = window.activeTextEditor;
        if (!activeEditor) {
          window.showErrorMessage("No file selected");
          return;
        }
        filePath = activeEditor.document.uri.fsPath;
      }

      // Validate file extension
      const ext = path.extname(filePath);
      const validExtensions = [".schema", ".xform", ".transform", ".proc", ".rules"];
      if (!validExtensions.includes(ext)) {
        window.showErrorMessage(
          `Invalid file type. Expected: ${validExtensions.join(", ")}`
        );
        return;
      }

      const result = await buildRunner.generateFile(filePath);

      if (result.success) {
        window.showInformationMessage(
          `Generated ${result.generatedFiles} Java file(s) from ${path.basename(filePath)}`
        );
      } else {
        window.showErrorMessage(
          `Generation failed. Check Output panel for details.`
        );
      }
    }
  );
  context.subscriptions.push(generateFileCommand);

  outputChannel.appendLine("Nexflow commands registered (build, validate, generate, visual designer)");
  } catch (error) {
    const errorMsg = `Nexflow extension activation failed: ${error}`;
    if (outputChannel) {
      outputChannel.appendLine(errorMsg);
    }
    window.showErrorMessage(errorMsg);
    throw error; // Re-throw to let VS Code know activation failed
  }
}

/**
 * Deactivate the extension.
 */
export async function deactivate(): Promise<void> {
  if (client) {
    await client.stop();
  }
}
