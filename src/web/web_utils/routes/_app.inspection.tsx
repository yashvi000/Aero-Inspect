import { createFileRoute } from "@tanstack/react-router";
import { InspectionPage } from "../../features/inspection/InspectionPage";

export const Route = createFileRoute("/_app/inspection")({
  head: () => ({ meta: [{ title: "Inspection — AeroInspect" }] }),
  component: InspectionPage,
});
