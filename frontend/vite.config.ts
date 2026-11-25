import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

import { pagesHeaders } from "./build/pagesHeaders.ts";

// index.html reads these (canonical URL, OG tags, preconnect). Defaults keep local builds valid.
process.env.VITE_SITE_URL ??= "http://localhost:5173";
process.env.VITE_API_BASE_URL ??= "http://localhost:8000";

export default defineConfig({
  plugins: [
    tanstackRouter({ target: "react", autoCodeSplitting: true }),
    react(),
    tailwindcss(),
    pagesHeaders(),
  ],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: { port: 5173, strictPort: true },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}", "build/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      include: ["src/**/*.{ts,tsx}", "build/**/*.ts"],
      exclude: [
        "src/**/*.test.{ts,tsx}",
        "build/**/*.test.ts",
        "src/test/**",
        "src/main.tsx",
        "src/routeTree.gen.ts",
        "src/lib/api/schema.d.ts",
        "src/components/ui/**",
      ],
      // QUALITY_GATES: frontend >= 80% lines overall, lib/ >= 90%.
      thresholds: {
        lines: 80,
        "src/lib/**": { lines: 90 },
      },
    },
  },
});
