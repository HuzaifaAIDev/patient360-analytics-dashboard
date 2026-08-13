import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Same policy as frontend/nginx.conf (production) — kept here too so
// `npm run preview` (serving the actual production build locally) behaves
// identically to the real deployment for testing purposes.
const PRODUCTION_CSP =
  "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " +
  "img-src 'self' data:; connect-src 'self'; font-src 'self' https://fonts.gstatic.com data:; " +
  "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'";

// Headers that are always safe to send, in dev or prod — none of these
// interfere with Vite's HMR client/websocket or module loading.
const SAFE_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
    // NOTE: no Content-Security-Policy here on purpose. Vite's dev server
    // (HMR client, on-the-fly module transforms, inline preamble scripts)
    // relies on patterns a strict CSP would block, and enforcing CSP is
    // fundamentally a production/deployed-page concern anyway — see
    // `preview.headers` below and frontend/nginx.conf for where it's
    // actually enforced, against the real production build.
    headers: SAFE_HEADERS,
  },
  preview: {
    // `npm run preview` serves the real production build, so it gets the
    // full production header set including CSP — a way to sanity-check the
    // policy locally before it's live behind nginx.
    headers: { ...SAFE_HEADERS, "Content-Security-Policy": PRODUCTION_CSP },
  },
});
