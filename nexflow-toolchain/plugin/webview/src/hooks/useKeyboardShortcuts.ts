/**
 * Keyboard Shortcuts Hook for Visual Designer
 *
 * Provides consistent keyboard handling across the canvas.
 * Respects platform conventions (Cmd on Mac, Ctrl on Windows/Linux).
 */

import { useEffect, useCallback } from "react";

interface ShortcutHandlers {
  onUndo?: () => void;
  onRedo?: () => void;
  onSave?: () => void;
  onDelete?: () => void;
  onSelectAll?: () => void;
  onEscape?: () => void;
  onCopy?: () => void;
  onPaste?: () => void;
}

interface UseKeyboardShortcutsOptions {
  enabled?: boolean;
}

/**
 * Detect if running on Mac for Cmd vs Ctrl
 */
const isMac =
  typeof navigator !== "undefined" &&
  navigator.platform.toUpperCase().indexOf("MAC") >= 0;

/**
 * Check if the meta/ctrl key is pressed based on platform
 */
function isModifierPressed(event: KeyboardEvent): boolean {
  return isMac ? event.metaKey : event.ctrlKey;
}

export function useKeyboardShortcuts(
  handlers: ShortcutHandlers,
  options: UseKeyboardShortcutsOptions = {}
): void {
  const { enabled = true } = options;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Don't trigger shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        // Allow Escape to still work in inputs
        if (event.key !== "Escape") {
          return;
        }
      }

      const modifier = isModifierPressed(event);
      const key = event.key.toLowerCase();

      // Undo: Cmd/Ctrl + Z (without Shift)
      if (modifier && key === "z" && !event.shiftKey) {
        event.preventDefault();
        handlers.onUndo?.();
        return;
      }

      // Redo: Cmd/Ctrl + Shift + Z or Cmd/Ctrl + Y
      if (modifier && ((key === "z" && event.shiftKey) || key === "y")) {
        event.preventDefault();
        handlers.onRedo?.();
        return;
      }

      // Save: Cmd/Ctrl + S
      if (modifier && key === "s") {
        event.preventDefault();
        handlers.onSave?.();
        return;
      }

      // Select All: Cmd/Ctrl + A
      if (modifier && key === "a") {
        event.preventDefault();
        handlers.onSelectAll?.();
        return;
      }

      // Copy: Cmd/Ctrl + C
      if (modifier && key === "c") {
        event.preventDefault();
        handlers.onCopy?.();
        return;
      }

      // Paste: Cmd/Ctrl + V
      if (modifier && key === "v") {
        event.preventDefault();
        handlers.onPaste?.();
        return;
      }

      // Delete: Delete or Backspace (no modifier)
      if (!modifier && (key === "delete" || key === "backspace")) {
        event.preventDefault();
        handlers.onDelete?.();
        return;
      }

      // Escape: Clear selection
      if (key === "escape") {
        event.preventDefault();
        handlers.onEscape?.();
        return;
      }
    },
    [enabled, handlers]
  );

  useEffect(() => {
    if (!enabled) return;

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, handleKeyDown]);
}

/**
 * Get display string for keyboard shortcut (for tooltips)
 */
export function getShortcutDisplay(shortcut: string): string {
  const modKey = isMac ? "⌘" : "Ctrl+";

  switch (shortcut) {
    case "undo":
      return `${modKey}Z`;
    case "redo":
      return isMac ? "⌘⇧Z" : "Ctrl+Y";
    case "save":
      return `${modKey}S`;
    case "selectAll":
      return `${modKey}A`;
    case "copy":
      return `${modKey}C`;
    case "paste":
      return `${modKey}V`;
    case "delete":
      return "Del";
    case "escape":
      return "Esc";
    default:
      return shortcut;
  }
}
