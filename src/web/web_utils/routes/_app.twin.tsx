import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Boxes, ArrowRight } from "lucide-react";
import { PageHeader } from "../../components/common/PageHeader";
import { useWorkflow } from "../../hooks/use_inspection";

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
        subtitle="3D digital twin of the airframe with detected defect overlays. Rendering handled by the existing twin viewer module."
      />

      <div className="flex min-h-[520px] items-center justify-center rounded-lg border border-dashed border-border bg-panel">
        <div className="max-w-md space-y-3 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
            <Boxes className="h-7 w-7" />
          </div>
          <div className="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
            Twin viewer mount point
          </div>
          <p className="text-sm text-muted-foreground">
            Drop the existing digital twin viewer component here. Defect at{" "}
            <span className="text-foreground">{detection.zone}</span> ({detection.defectType},{" "}
            {(detection.confidence * 100).toFixed(1)}%) is available via the workflow store.
          </p>
        </div>
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
