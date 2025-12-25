// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * Visual Designer Panel
 *
 * Manages the WebviewPanel for the Nexflow Visual Designer.
 * Handles lifecycle, messaging, and CLI integration.
 */

import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { spawn } from "child_process";
import {
  getNexflowRuntime,
  buildCommandArgs,
  getProcessEnv,
  NexflowRuntime,
} from "../runtime";

export class VisualDesignerPanel {
  public static currentPanel: VisualDesignerPanel | undefined;
  public static readonly viewType = "nexflow.visualDesigner";

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private readonly _projectRoot: string;
  private _runtime: NexflowRuntime | null = null;
  private _procFilePath: string | undefined;
  private _disposables: vscode.Disposable[] = [];

  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    projectRoot: string
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._projectRoot = projectRoot;

    // Set webview content
    this._update();

    // Handle messages from webview
    this._panel.webview.onDidReceiveMessage(
      (message) => this._handleMessage(message),
      null,
      this._disposables
    );

    // Handle panel disposal
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  /**
   * Create or show the Visual Designer panel.
   */
  public static createOrShow(
    extensionUri: vscode.Uri,
    projectRoot: string,
    procFilePath?: string
  ): VisualDesignerPanel {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If panel exists, show it
    if (VisualDesignerPanel.currentPanel) {
      VisualDesignerPanel.currentPanel._panel.reveal(column);
      if (procFilePath) {
        VisualDesignerPanel.currentPanel.loadProcFile(procFilePath);
      }
      return VisualDesignerPanel.currentPanel;
    }

    // Create new panel
    const panel = vscode.window.createWebviewPanel(
      VisualDesignerPanel.viewType,
      "Nexflow Visual Designer",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.joinPath(extensionUri, "webview", "dist"),
          vscode.Uri.joinPath(extensionUri, "out"),
        ],
      }
    );

    VisualDesignerPanel.currentPanel = new VisualDesignerPanel(
      panel,
      extensionUri,
      projectRoot
    );

    if (procFilePath) {
      VisualDesignerPanel.currentPanel.loadProcFile(procFilePath);
    }

    return VisualDesignerPanel.currentPanel;
  }

  /**
   * Load a .proc file into the designer.
   * Checks for existing .proc.ui file and validates sync state.
   */
  public async loadProcFile(filePath: string): Promise<void> {
    this._procFilePath = filePath;
    this._panel.title = `Visual Designer - ${path.basename(filePath)}`;

    try {
      // Parse the .proc file to get current graph
      const graphData = await this._parseToGraph(filePath);
      const currentChecksum = (graphData as any).metadata?.graphChecksum || "";

      // Check if .proc.ui file exists
      const uiFilePath = `${filePath}.ui`;
      let savedLayout: any = null;
      let syncStatus: "synced" | "out_of_sync" | "no_ui_file" = "no_ui_file";

      if (fs.existsSync(uiFilePath)) {
        try {
          const uiContent = JSON.parse(fs.readFileSync(uiFilePath, "utf-8"));
          const savedChecksum = uiContent.metadata?.graphChecksum || "";

          if (savedChecksum === currentChecksum) {
            // Checksums match - use saved layout
            syncStatus = "synced";
            savedLayout = uiContent;
          } else {
            // Checksums don't match - ask user
            syncStatus = "out_of_sync";
            const choice = await vscode.window.showWarningMessage(
              "The .proc file has been modified since the visual layout was last saved. What would you like to do?",
              { modal: true },
              "Regenerate Layout",
              "Keep Existing Layout"
            );

            if (choice === "Keep Existing Layout") {
              savedLayout = uiContent;
            }
            // If "Regenerate Layout" or dismissed, savedLayout stays null (use fresh layout)
          }
        } catch (e) {
          // Invalid .proc.ui file - regenerate
          vscode.window.showWarningMessage(
            "Layout file is corrupted. Regenerating layout."
          );
        }
      }

      // Send graph data to webview with layout info
      this._panel.webview.postMessage({
        type: "loadGraph",
        data: graphData,
        filePath: filePath,
        savedLayout: savedLayout,
        syncStatus: syncStatus,
      });
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to load ${filePath}: ${error}`);
      this._panel.webview.postMessage({
        type: "error",
        message: `Failed to load file: ${error}`,
      });
    }
  }

  /**
   * Initialize runtime detection (call before running commands)
   */
  private async _ensureRuntime(): Promise<NexflowRuntime> {
    if (!this._runtime) {
      this._runtime = await getNexflowRuntime();
    }
    return this._runtime;
  }

  /**
   * Parse .proc file to graph format using CLI.
   */
  private async _parseToGraph(filePath: string): Promise<object> {
    const runtime = await this._ensureRuntime();

    return new Promise((resolve, reject) => {
      const args = buildCommandArgs("parse", [filePath, "--format", "graph"], {
        runtime,
        addDebugFlag: runtime.developerMode,
      });

      const proc = spawn(runtime.command, args, {
        cwd: this._projectRoot,
        env: getProcessEnv(runtime),
      });

      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("close", (code) => {
        if (code === 0) {
          try {
            const graphData = JSON.parse(stdout);
            resolve(graphData);
          } catch (e) {
            reject(`Failed to parse graph output: ${e}`);
          }
        } else {
          reject(stderr || `Process exited with code ${code}`);
        }
      });

      proc.on("error", (err) => {
        reject(`Failed to spawn process: ${err.message}`);
      });
    });
  }

  /**
   * Handle messages from the webview.
   */
  private async _handleMessage(message: any): Promise<void> {
    switch (message.type) {
      case "ready":
        // Webview is ready, load file if we have one
        if (this._procFilePath) {
          await this.loadProcFile(this._procFilePath);
        }
        break;

      case "save":
        // Save canvas state to .proc.ui file with metadata
        if (this._procFilePath) {
          const uiFilePath = `${this._procFilePath}.ui`;
          try {
            // Get current graph checksum from parsed data
            const graphData = await this._parseToGraph(this._procFilePath);
            const graphChecksum = (graphData as any).metadata?.graphChecksum || "";

            // Structure the .proc.ui file with metadata
            const uiFileContent = {
              metadata: {
                version: "1.0",
                procFile: path.basename(this._procFilePath),
                graphChecksum: graphChecksum,
                savedAt: new Date().toISOString(),
              },
              ...message.data,
            };

            fs.writeFileSync(uiFilePath, JSON.stringify(uiFileContent, null, 2));
            vscode.window.showInformationMessage(`Saved ${path.basename(uiFilePath)}`);
          } catch (error) {
            vscode.window.showErrorMessage(`Failed to save: ${error}`);
          }
        }
        break;

      case "openInEditor":
        // Open the .proc file in VS Code editor
        if (this._procFilePath) {
          const doc = await vscode.workspace.openTextDocument(this._procFilePath);
          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        }
        break;

      case "openTransform":
        // Open a transform file in VS Code
        await this._openDslFile(message.name, ".xform");
        break;

      case "openRules":
        // Open a rules file in VS Code
        await this._openDslFile(message.name, ".rules");
        break;

      case "validate":
        // Validate current file
        if (this._procFilePath) {
          await this._validateFile(this._procFilePath);
        }
        break;

      case "generatedDsl":
        // Handle generated DSL from visual authoring
        await this._handleGeneratedDsl(message.data);
        break;

      case "exportCanvas":
        // Export canvas as PNG or SVG to the same directory as .proc file
        await this._handleExportCanvas(message.format, message.data);
        break;

      case "exportError":
        // Show export error from webview
        vscode.window.showErrorMessage(message.message);
        break;
    }
  }

  /**
   * Handle generated DSL from visual authoring.
   * Shows the DSL in a new untitled document or saves to existing file.
   */
  private async _handleGeneratedDsl(dslContent: string): Promise<void> {
    if (this._procFilePath) {
      // Ask user what to do
      const choice = await vscode.window.showQuickPick(
        [
          { label: "Update existing file", description: this._procFilePath },
          { label: "Open in new editor", description: "Preview without saving" },
          { label: "Save as new file...", description: "Create a new .proc file" },
        ],
        { placeHolder: "What would you like to do with the generated DSL?" }
      );

      if (!choice) return;

      if (choice.label === "Update existing file") {
        try {
          fs.writeFileSync(this._procFilePath, dslContent);
          vscode.window.showInformationMessage(`Updated ${path.basename(this._procFilePath)}`);
          // Refresh the file in editor if open
          const doc = await vscode.workspace.openTextDocument(this._procFilePath);
          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
          vscode.window.showErrorMessage(`Failed to save: ${error}`);
        }
      } else if (choice.label === "Open in new editor") {
        const doc = await vscode.workspace.openTextDocument({
          content: dslContent,
          language: "nexflow",
        });
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
      } else if (choice.label === "Save as new file...") {
        await this._saveAsNewFile(dslContent);
      }
    } else {
      // No existing file, ask to save
      const choice = await vscode.window.showQuickPick(
        [
          { label: "Save as new file...", description: "Create a new .proc file" },
          { label: "Open in new editor", description: "Preview without saving" },
        ],
        { placeHolder: "What would you like to do with the generated DSL?" }
      );

      if (!choice) return;

      if (choice.label === "Save as new file...") {
        await this._saveAsNewFile(dslContent);
      } else {
        const doc = await vscode.workspace.openTextDocument({
          content: dslContent,
          language: "nexflow",
        });
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
      }
    }
  }

  /**
   * Save DSL content as a new .proc file.
   */
  private async _saveAsNewFile(dslContent: string): Promise<void> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    const defaultUri = workspaceFolder
      ? vscode.Uri.joinPath(workspaceFolder.uri, "new_process.proc")
      : undefined;

    const uri = await vscode.window.showSaveDialog({
      defaultUri,
      filters: { "Nexflow Process": ["proc"] },
      title: "Save Process DSL",
    });

    if (uri) {
      try {
        fs.writeFileSync(uri.fsPath, dslContent);
        vscode.window.showInformationMessage(`Saved ${path.basename(uri.fsPath)}`);
        this._procFilePath = uri.fsPath;
        this._panel.title = `Visual Designer - ${path.basename(uri.fsPath)}`;
        // Open the new file in editor
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to save: ${error}`);
      }
    }
  }

  /**
   * Handle canvas export (PNG or SVG).
   * Saves to the same directory as the .proc file.
   */
  private async _handleExportCanvas(format: "png" | "svg", dataUrl: string): Promise<void> {
    if (!this._procFilePath) {
      vscode.window.showErrorMessage("No .proc file open. Save your process first.");
      return;
    }

    try {
      // Generate export filename based on .proc file
      const procDir = path.dirname(this._procFilePath);
      const procBasename = path.basename(this._procFilePath, ".proc");
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      const exportFileName = `${procBasename}_${timestamp}.${format}`;
      const exportPath = path.join(procDir, exportFileName);

      // Extract base64 data from data URL
      const base64Data = dataUrl.split(",")[1];
      if (!base64Data) {
        throw new Error("Invalid data URL format");
      }

      // Write file
      const buffer = Buffer.from(base64Data, "base64");
      fs.writeFileSync(exportPath, buffer);

      vscode.window.showInformationMessage(`Exported: ${exportFileName}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to export ${format.toUpperCase()}: ${error}`);
    }
  }

  /**
   * Find and open a DSL file by name.
   * First looks in the same directory as the .proc file, then searches workspace.
   * Also tries partial name matching if exact match not found.
   */
  private async _openDslFile(name: string, extension: string): Promise<void> {
    const fileName = `${name}${extension}`;

    // First, check if file exists in same directory as the .proc file
    if (this._procFilePath) {
      const procDir = path.dirname(this._procFilePath);

      // Try exact match first
      const exactPath = path.join(procDir, fileName);
      if (fs.existsSync(exactPath)) {
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(exactPath));
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        return;
      }

      // Try to find any file with the extension in the same directory
      try {
        const dirFiles = fs.readdirSync(procDir);
        const matchingFiles = dirFiles.filter(f => f.endsWith(extension));

        if (matchingFiles.length === 1) {
          // Only one file of this type - open it
          const filePath = path.join(procDir, matchingFiles[0]);
          const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(filePath));
          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
          return;
        } else if (matchingFiles.length > 1) {
          // Multiple files - show quick pick
          const selected = await vscode.window.showQuickPick(matchingFiles, {
            placeHolder: `Select ${extension} file (looking for "${name}")`,
          });
          if (selected) {
            const filePath = path.join(procDir, selected);
            const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(filePath));
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            return;
          }
          return; // User cancelled
        }
      } catch (e) {
        // Directory read failed, continue to workspace search
      }
    }

    // Fall back to workspace search
    const pattern = `**/${fileName}`;
    const files = await vscode.workspace.findFiles(pattern, "**/node_modules/**", 1);

    if (files.length > 0) {
      const doc = await vscode.workspace.openTextDocument(files[0]);
      await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
    } else {
      // Try broader search for any file with the extension
      const broadPattern = `**/*${extension}`;
      const broadFiles = await vscode.workspace.findFiles(broadPattern, "**/node_modules/**", 10);

      if (broadFiles.length > 0) {
        const fileNames = broadFiles.map(f => path.basename(f.fsPath));
        const selected = await vscode.window.showQuickPick(fileNames, {
          placeHolder: `"${fileName}" not found. Select a ${extension} file:`,
        });
        if (selected) {
          const selectedFile = broadFiles.find(f => path.basename(f.fsPath) === selected);
          if (selectedFile) {
            const doc = await vscode.workspace.openTextDocument(selectedFile);
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            return;
          }
        }
      } else {
        vscode.window.showWarningMessage(
          `Could not find ${fileName}. No ${extension} files found in workspace.`
        );
      }
    }
  }

  /**
   * Validate a .proc file using CLI.
   */
  private async _validateFile(filePath: string): Promise<void> {
    const runtime = await this._ensureRuntime();

    return new Promise((resolve) => {
      const args = buildCommandArgs("validate", [filePath], {
        runtime,
        addDebugFlag: runtime.developerMode,
      });

      const proc = spawn(runtime.command, args, {
        cwd: this._projectRoot,
        env: getProcessEnv(runtime),
      });

      let stderr = "";

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("close", (code) => {
        if (code === 0) {
          vscode.window.showInformationMessage("Validation passed");
          this._panel.webview.postMessage({ type: "validationResult", success: true });
        } else {
          vscode.window.showErrorMessage(`Validation failed: ${stderr}`);
          this._panel.webview.postMessage({
            type: "validationResult",
            success: false,
            errors: stderr,
          });
        }
        resolve();
      });
    });
  }

  /**
   * Update the webview content.
   */
  private _update(): void {
    this._panel.webview.html = this._getHtmlForWebview();
  }

  /**
   * Generate HTML for the webview.
   */
  private _getHtmlForWebview(): string {
    const webview = this._panel.webview;

    // Check if built webview exists
    const distPath = vscode.Uri.joinPath(this._extensionUri, "webview", "dist", "index.js");
    const distExists = fs.existsSync(distPath.fsPath);

    if (distExists) {
      // Production: load bundled React app
      const scriptUri = webview.asWebviewUri(distPath);
      const styleUri = webview.asWebviewUri(
        vscode.Uri.joinPath(this._extensionUri, "webview", "dist", "index.css")
      );

      return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src ${webview.cspSource};">
  <link href="${styleUri}" rel="stylesheet">
  <title>Nexflow Visual Designer</title>
</head>
<body>
  <div id="root"></div>
  <script src="${scriptUri}"></script>
</body>
</html>`;
    } else {
      // Development: show placeholder
      return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nexflow Visual Designer</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    .container {
      text-align: center;
      max-width: 600px;
    }
    h1 {
      color: var(--vscode-textLink-foreground);
      margin-bottom: 10px;
    }
    .status {
      background: var(--vscode-textBlockQuote-background);
      border-left: 3px solid var(--vscode-textLink-foreground);
      padding: 15px;
      margin: 20px 0;
      text-align: left;
    }
    .file-info {
      font-family: var(--vscode-editor-font-family);
      background: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 4px;
      margin: 10px 0;
    }
    button {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 8px 16px;
      cursor: pointer;
      margin: 5px;
      border-radius: 2px;
    }
    button:hover {
      background: var(--vscode-button-hoverBackground);
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Nexflow Visual Designer</h1>
    <p>React Flow canvas for L1 Process topology design</p>

    <div class="status">
      <strong>Status:</strong> Development Mode<br>
      <small>Webview not yet built. Run <code>npm run build:webview</code> in the plugin directory.</small>
    </div>

    <div id="file-info" class="file-info" style="display: none;">
      <strong>File:</strong> <span id="filename"></span>
    </div>

    <div id="graph-data" style="display: none;"></div>

    <div>
      <button onclick="openInEditor()">Open in Editor</button>
      <button onclick="validate()">Validate</button>
    </div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    // Tell extension we're ready
    vscode.postMessage({ type: 'ready' });

    // Handle messages from extension
    window.addEventListener('message', event => {
      const message = event.data;

      switch (message.type) {
        case 'loadGraph':
          document.getElementById('file-info').style.display = 'block';
          document.getElementById('filename').textContent = message.filePath;
          document.getElementById('graph-data').textContent = JSON.stringify(message.data, null, 2);
          console.log('Graph loaded:', message.data);
          break;

        case 'error':
          alert(message.message);
          break;
      }
    });

    function openInEditor() {
      vscode.postMessage({ type: 'openInEditor' });
    }

    function validate() {
      vscode.postMessage({ type: 'validate' });
    }
  </script>
</body>
</html>`;
    }
  }

  /**
   * Dispose of resources.
   */
  public dispose(): void {
    VisualDesignerPanel.currentPanel = undefined;

    this._panel.dispose();

    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }
}
