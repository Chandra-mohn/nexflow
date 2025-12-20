/**
 * VS Code API wrapper for webview communication.
 */

interface VSCodeApi {
  postMessage(message: unknown): void;
  getState(): unknown;
  setState(state: unknown): void;
}

// Declare the VS Code injected global
declare function acquireVsCodeApi(): VSCodeApi;

// Acquire VS Code API (only available in VS Code webview context)
function getVSCodeApi(): VSCodeApi {
  if (typeof acquireVsCodeApi === "function") {
    return acquireVsCodeApi();
  }

  // Mock for development outside VS Code
  console.warn("Running outside VS Code - using mock API");
  return {
    postMessage: (message: unknown) => {
      console.log("Mock postMessage:", message);
    },
    getState: () => ({}),
    setState: (state: unknown) => {
      console.log("Mock setState:", state);
    },
  };
}

export const vscodeApi = getVSCodeApi();
