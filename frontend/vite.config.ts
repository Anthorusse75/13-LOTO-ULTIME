import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (err, req) => {
            console.error(
              `[PROXY ERROR] ${req.method} ${req.url} →`,
              err.message,
            );
          });
          proxy.on("proxyRes", (proxyRes, req) => {
            // Réécrire les headers Location pour que les redirects passent par le proxy
            const location = proxyRes.headers["location"];
            if (
              location &&
              (location.includes("localhost:8000") ||
                location.includes("127.0.0.1:8000"))
            ) {
              proxyRes.headers["location"] = location
                .replace(/https?:\/\/localhost:8000/, "")
                .replace(/https?:\/\/127\.0\.0\.1:8000/, "");
              console.log(
                `[PROXY REDIRECT REWRITTEN] ${req.url} → ${proxyRes.headers["location"]}`,
              );
            }
          });
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
    exclude: ["e2e/**", "node_modules/**"],
  },
});
