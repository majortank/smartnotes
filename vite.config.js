import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  root: path.resolve(__dirname),
  build: {
    outDir: "static/dist",
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      input: {
        tiptap: path.resolve(__dirname, "frontend/tiptap.js"),
      },
      output: {
        entryFileNames: "tiptap.js",
        assetFileNames: "tiptap.[ext]",
      },
    },
  },
  server: {
    strictPort: true,
  },
});
