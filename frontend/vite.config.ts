import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// В dev-режиме запросы /api и /health проксируются на бэкенд,
// поэтому CORS не мешает и baseURL на клиенте может быть пустым.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: process.env.VITE_PROXY_TARGET || "http://localhost:8000", changeOrigin: true },
      "/health": { target: process.env.VITE_PROXY_TARGET || "http://localhost:8000", changeOrigin: true },
    },
  },
});
