import { createFileRoute } from "@tanstack/react-router";
import { AnalysisPage } from "../../features/analysis/AnalysisPage";

export const Route = createFileRoute("/_app/analysis")({
  head: () => ({ meta: [{ title: "Analysis — AeroInspect" }] }),
  component: AnalysisPage,
});
