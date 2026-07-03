import { createFileRoute } from "@tanstack/react-router";
import { ReportsPage } from "../../features/reports/ReportsPage";

export const Route = createFileRoute("/_app/reports")({
  head: () => ({ meta: [{ title: "Reports — AeroInspect" }] }),
  component: ReportsPage,
});
