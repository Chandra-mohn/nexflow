/**
 * Canvas Export Utilities
 *
 * Export React Flow canvas as PNG or SVG.
 * Files are saved to the same directory as the .proc file.
 */

import { toPng, toSvg } from "html-to-image";
import { vscodeApi } from "../vscode";

export type ExportFormat = "png" | "svg";

interface ExportOptions {
  /** Background color (default: transparent for SVG, white for PNG) */
  backgroundColor?: string;
  /** Scale factor for higher resolution PNG (default: 2) */
  scale?: number;
  /** Include padding around the canvas */
  padding?: number;
}

/**
 * Get the React Flow viewport element for export.
 */
function getReactFlowElement(): HTMLElement | null {
  // React Flow renders into a div with class "react-flow__viewport"
  // We want the parent container that includes the viewport
  const viewport = document.querySelector(".react-flow__viewport");
  if (!viewport) {
    console.error("React Flow viewport not found");
    return null;
  }

  // Get the react-flow container (parent of viewport)
  const container = viewport.closest(".react-flow");
  return container as HTMLElement | null;
}

/**
 * Export canvas as PNG and send to VS Code extension for saving.
 */
export async function exportAsPng(options: ExportOptions = {}): Promise<void> {
  const { backgroundColor = "#ffffff", scale = 2, padding = 20 } = options;

  const element = getReactFlowElement();
  if (!element) {
    vscodeApi.postMessage({
      type: "exportError",
      message: "Could not find canvas element to export",
    });
    return;
  }

  try {
    const dataUrl = await toPng(element, {
      backgroundColor,
      pixelRatio: scale,
      style: {
        padding: `${padding}px`,
      },
    });

    // Send data URL to extension for file saving
    vscodeApi.postMessage({
      type: "exportCanvas",
      format: "png",
      data: dataUrl,
    });
  } catch (error) {
    console.error("Failed to export PNG:", error);
    vscodeApi.postMessage({
      type: "exportError",
      message: `Failed to export PNG: ${error}`,
    });
  }
}

/**
 * Export canvas as SVG and send to VS Code extension for saving.
 */
export async function exportAsSvg(options: ExportOptions = {}): Promise<void> {
  const { backgroundColor, padding = 20 } = options;

  const element = getReactFlowElement();
  if (!element) {
    vscodeApi.postMessage({
      type: "exportError",
      message: "Could not find canvas element to export",
    });
    return;
  }

  try {
    const dataUrl = await toSvg(element, {
      backgroundColor: backgroundColor || "transparent",
      style: {
        padding: `${padding}px`,
      },
    });

    // Send data URL to extension for file saving
    vscodeApi.postMessage({
      type: "exportCanvas",
      format: "svg",
      data: dataUrl,
    });
  } catch (error) {
    console.error("Failed to export SVG:", error);
    vscodeApi.postMessage({
      type: "exportError",
      message: `Failed to export SVG: ${error}`,
    });
  }
}

/**
 * Export canvas in specified format.
 */
export async function exportCanvas(
  format: ExportFormat,
  options: ExportOptions = {}
): Promise<void> {
  if (format === "png") {
    await exportAsPng(options);
  } else if (format === "svg") {
    await exportAsSvg(options);
  } else {
    console.error(`Unknown export format: ${format}`);
  }
}
