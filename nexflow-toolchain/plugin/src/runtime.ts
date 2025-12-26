// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * Runtime Detection Module
 *
 * Provides unified runtime detection for Nexflow CLI invocation.
 * Supports both standalone executable (nexflow.exe) and Python module modes.
 *
 * Detection Priority:
 * 1. User setting: nexflow.runtime.usePython (force Python mode)
 * 2. User setting: nexflow.runtime.executable (explicit path)
 * 3. Auto-detect: nexflow.exe in system PATH
 * 4. Fallback: python -m nexflow
 */

import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";
import { execSync } from "child_process";

/**
 * Runtime configuration for spawning Nexflow processes
 */
export interface NexflowRuntime {
  /** The command to execute (path to exe or python interpreter) */
  command: string;
  /** Base arguments (empty for exe, ["-m", "nexflow"] for Python) */
  baseArgs: string[];
  /** Whether running in Python mode */
  isPythonMode: boolean;
  /** Whether developer mode is enabled (adds --debug flag) */
  developerMode: boolean;
  /** The detected runtime source for logging */
  source: "setting" | "path" | "fallback";
}

/**
 * Cache for runtime detection (cleared on config change)
 */
let cachedRuntime: NexflowRuntime | null = null;

/**
 * Clear the runtime cache (call when settings change)
 */
export function clearRuntimeCache(): void {
  cachedRuntime = null;
}

/**
 * Detect nexflow.exe in system PATH
 */
function detectExeInPath(): string | null {
  try {
    // Windows: use 'where' command
    if (process.platform === "win32") {
      const result = execSync("where nexflow.exe", {
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      const lines = result.trim().split("\n");
      if (lines.length > 0 && lines[0].trim()) {
        const exePath = lines[0].trim();
        if (fs.existsSync(exePath)) {
          return exePath;
        }
      }
    }
    // macOS/Linux: use 'which' command
    else {
      const result = execSync("which nexflow", {
        encoding: "utf-8",
        stdio: ["pipe", "pipe", "pipe"],
      });
      const exePath = result.trim();
      if (exePath && fs.existsSync(exePath)) {
        return exePath;
      }
    }
  } catch {
    // Command failed - exe not in PATH
  }
  return null;
}

/**
 * Get the Python interpreter path from settings
 */
function getPythonPath(): string {
  const config = vscode.workspace.getConfiguration("nexflow");
  const pythonPath = config.get<string>("pythonPath", "");

  if (pythonPath && pythonPath.trim()) {
    return pythonPath.trim();
  }

  // Try to get from Python extension
  const pythonConfig = vscode.workspace.getConfiguration("python");
  const pythonInterpreter = pythonConfig.get<string>("defaultInterpreterPath", "");

  if (pythonInterpreter && pythonInterpreter.trim()) {
    return pythonInterpreter.trim();
  }

  // Default fallback
  return process.platform === "win32" ? "python" : "python3";
}

/**
 * Get the Nexflow project root (toolchain directory)
 * Used for PYTHONPATH when running in Python mode
 */
export function getToolchainRoot(): string {
  const config = vscode.workspace.getConfiguration("nexflow");
  const toolchainPath = config.get<string>("toolchainPath", "");

  if (toolchainPath && toolchainPath.trim()) {
    return toolchainPath.trim();
  }

  // Try to find nexflow-toolchain in common locations
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (workspaceFolders) {
    for (const folder of workspaceFolders) {
      // Check if this is the toolchain itself
      const nexflowToml = path.join(folder.uri.fsPath, "nexflow.toml");
      const backendDir = path.join(folder.uri.fsPath, "backend");
      if (fs.existsSync(nexflowToml) && fs.existsSync(backendDir)) {
        return folder.uri.fsPath;
      }

      // Check for nexflow-toolchain subdirectory
      const toolchainSubdir = path.join(folder.uri.fsPath, "nexflow-toolchain");
      if (fs.existsSync(toolchainSubdir)) {
        return toolchainSubdir;
      }
    }
  }

  // Fallback: use extension's parent directory structure
  return "";
}

/**
 * Detect and return the appropriate Nexflow runtime configuration.
 *
 * @returns Runtime configuration for spawning Nexflow processes
 */
export async function getNexflowRuntime(): Promise<NexflowRuntime> {
  // Return cached runtime if available
  if (cachedRuntime) {
    return cachedRuntime;
  }

  const config = vscode.workspace.getConfiguration("nexflow");
  const developerMode = config.get<boolean>("runtime.developerMode", false);

  // Priority 1: User explicitly wants Python mode
  const forcePython = config.get<boolean>("runtime.usePython", false);
  if (forcePython) {
    cachedRuntime = {
      command: getPythonPath(),
      baseArgs: ["-m", "nexflow"],
      isPythonMode: true,
      developerMode,
      source: "setting",
    };
    return cachedRuntime;
  }

  // Priority 2: User specified explicit executable path
  const explicitExe = config.get<string>("runtime.executable", "");
  if (explicitExe && explicitExe.trim()) {
    const exePath = explicitExe.trim();
    if (fs.existsSync(exePath)) {
      cachedRuntime = {
        command: exePath,
        baseArgs: [],
        isPythonMode: false,
        developerMode,
        source: "setting",
      };
      return cachedRuntime;
    } else {
      // Warn user about invalid path
      vscode.window.showWarningMessage(
        `Nexflow executable not found at: ${exePath}. Falling back to Python mode.`
      );
    }
  }

  // Priority 3: Auto-detect nexflow.exe in PATH
  const pathExe = detectExeInPath();
  if (pathExe) {
    cachedRuntime = {
      command: pathExe,
      baseArgs: [],
      isPythonMode: false,
      developerMode,
      source: "path",
    };
    return cachedRuntime;
  }

  // Priority 4: Fallback to Python module
  cachedRuntime = {
    command: getPythonPath(),
    baseArgs: ["-m", "nexflow"],
    isPythonMode: true,
    developerMode,
    source: "fallback",
  };
  return cachedRuntime;
}

/**
 * Build command arguments for a Nexflow CLI invocation.
 *
 * @param subcommand The CLI subcommand (e.g., "parse", "build")
 * @param args Additional arguments for the subcommand
 * @param options Options for argument building
 * @returns Complete argument array for spawn()
 */
export function buildCommandArgs(
  subcommand: string,
  args: string[],
  options: {
    runtime: NexflowRuntime;
    addDebugFlag?: boolean;
  }
): string[] {
  const { runtime, addDebugFlag = false } = options;
  const result = [...runtime.baseArgs, subcommand, ...args];

  // Add debug flag if in developer mode and requested
  if (runtime.developerMode && addDebugFlag) {
    result.push("--debug");
  }

  return result;
}

/**
 * Get the full nexflow command as a single string.
 * Useful for terminal commands where you need a simple invocation string.
 *
 * @returns Command string like "nexflow" or "python3 -m nexflow"
 */
export async function getNexflowCommand(): Promise<string> {
  const runtime = await getNexflowRuntime();
  if (runtime.isPythonMode) {
    return `${runtime.command} ${runtime.baseArgs.join(' ')}`;
  }
  return runtime.command;
}

/**
 * Get environment variables for Nexflow process execution.
 * Adds PYTHONPATH when running in Python mode.
 */
export function getProcessEnv(runtime: NexflowRuntime): NodeJS.ProcessEnv {
  const env = { ...process.env };

  if (runtime.isPythonMode) {
    const toolchainRoot = getToolchainRoot();
    if (toolchainRoot) {
      env.PYTHONPATH = toolchainRoot;
    }
  }

  return env;
}

/**
 * Log runtime detection result for debugging
 */
export function logRuntimeInfo(
  runtime: NexflowRuntime,
  outputChannel?: vscode.OutputChannel
): void {
  const modeLabel = runtime.isPythonMode ? "Python module" : "Executable";
  const sourceLabel =
    runtime.source === "setting"
      ? "user setting"
      : runtime.source === "path"
        ? "PATH detection"
        : "fallback";

  const message = `[INFO] Nexflow runtime: ${modeLabel} (${sourceLabel})`;

  if (outputChannel) {
    outputChannel.appendLine(message);
    outputChannel.appendLine(`[INFO]   Command: ${runtime.command}`);
    if (runtime.baseArgs.length > 0) {
      outputChannel.appendLine(`[INFO]   Base args: ${runtime.baseArgs.join(" ")}`);
    }
    if (runtime.developerMode) {
      outputChannel.appendLine("[INFO]   Developer mode: enabled");
    }
  }
}
