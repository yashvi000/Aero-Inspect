import { createFileRoute } from "@tanstack/react-router";
import { LoginForm } from "../../features/auth/LoginForm";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — AeroInspect" },
      { name: "description", content: "Sign in to the AeroInspect Boeing 737 inspection console." },
    ],
  }),
  component: LoginForm,
});
