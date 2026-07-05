import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";


export default defineConfig({
  publicDir: "web/public",

  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    tanstackStart({
      srcDirectory: "web",
      server: { entry: "server" },
      router: {
        entry: "router",
        routesDirectory: "web_utils/routes",
        generatedRouteTree: "routeTree.gen.ts",
      },
      start: {
        entry: "start",
      },
    }),
    react(),
  ],

  server: {
    port: 8080,
  },
});