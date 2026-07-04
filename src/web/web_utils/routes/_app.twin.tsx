import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { PageHeader } from "../../components/common/PageHeader";
import { useWorkflow } from "../../hooks/use_inspection";
import DigitalTwinFeature from "../../features/twin";

export const Route = createFileRoute("/_app/twin")({
  head: () => ({ meta: [{ title: "Digital Twin — AeroInspect" }] }),
  component: DigitalTwinPage,
});

function DigitalTwinPage() {
  const navigate = useNavigate();
  const { detection, inspectionId } = useWorkflow();

  if (!detection || !inspectionId) {
    return (
      <div className="rounded-lg border border-border bg-panel p-10 text-center text-muted-foreground">
        No active inspection. Start from the{" "}
        <button
          onClick={() => navigate({ to: "/inspection" })}
          className="text-primary underline-offset-4 hover:underline"
        >
          Inspection
        </button>{" "}
        tab.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Step 02 / 04"
        title="Digital Twin"
        subtitle="3D digital twin of the airframe with detected defect overlays. Click zones to view details."
      />

      <div className="rounded-lg border border-border bg-panel overflow-hidden">
        <DigitalTwinFeature />
      </div>

      <div className="flex justify-end border-t border-border pt-5">
        <button
          onClick={() => navigate({ to: "/analysis" })}
          className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Continue to Analysis
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
