import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: resolve(__dirname, "src/main.tsx"),
      output: {
        entryFileNames: "index.js",
        assetFileNames: "index.[ext]",
        // Single bundle for VS Code webview
        manualChunks: undefined,
      },
    },
    // Inline assets for simpler webview loading
    assetsInlineLimit: 100000,
    // Don't use hashes in filenames
    cssCodeSplit: false,
  },
  // Base path for VS Code webview
  base: "",
});
