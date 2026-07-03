
import { defineConfig } from "@app.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    srcDirectory: "web",
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this
    server: { entry: "server" },
    router: {
      entry: "router",
      routesDirectory: "web_utils/routes",
      generatedRouteTree: "routeTree.gen.ts",
    },

    start: {
      entry: "start",
    },
  },
});
