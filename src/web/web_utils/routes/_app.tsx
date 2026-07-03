import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { AppShell } from "../../components/layout/app-shell";
import { useAuth } from "../../hooks/use_auths";

export const Route = createFileRoute("/_app")({
  beforeLoad: () => {
    if (typeof window !== "undefined" && !useAuth.getState().user) {
      throw redirect({ to: "/login" });
    }
  },
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
});
