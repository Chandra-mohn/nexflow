/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // VS Code theme colors (will use CSS variables)
        vscode: {
          bg: "var(--vscode-editor-background)",
          fg: "var(--vscode-editor-foreground)",
          border: "var(--vscode-panel-border)",
          accent: "var(--vscode-textLink-foreground)",
          button: "var(--vscode-button-background)",
          "button-fg": "var(--vscode-button-foreground)",
          input: "var(--vscode-input-background)",
          "input-fg": "var(--vscode-input-foreground)",
          "input-border": "var(--vscode-input-border)",
          sidebar: "var(--vscode-sideBar-background)",
        },
      },
    },
  },
  plugins: [],
};
