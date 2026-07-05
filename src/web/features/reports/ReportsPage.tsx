import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  FileText,
  Download,
  ClipboardList,
  Lock,
  RotateCcw,
  CheckCircle2,
  Flag,
  AlertTriangle,
  ArrowLeft,
  X,
} from "lucide-react";
import { useWorkflow } from "../../hooks/use_inspection";
import { PageHeader } from "../../components/common/PageHeader";

export function ReportsPage() {
  const navigate = useNavigate();
  const {
    inspectionId,
    detection,
    analysis,
    reports,
    approvedAnalysis,
    reportApproval,
    approveReports,
    flagReports,
    resetReportApproval,
    reset,
  } = useWorkflow();

  const [flagOpen, setFlagOpen] = useState(false);
  const [approveNotes, setApproveNotes] = useState("");
  const [flagReason, setFlagReason] = useState("");

  if (!detection || !inspectionId) {
    return (
      <div className="rounded-lg border border-border bg-panel p-10 text-center text-muted-foreground">
        No active inspection.{" "}
        <button
          onClick={() => navigate({ to: "/inspection" })}
          className="text-primary underline-offset-4 hover:underline"
        >
          Start a new inspection
        </button>
        .
      </div>
    );
  }

  const locked = !approvedAnalysis;
  const finalized = reportApproval.status === "approved";
  const flagged = reportApproval.status === "flagged";

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Step 04 / 04"
        title="Repair Plan &amp; Reports"
        subtitle="Review the generated repair plan and compliance documents. Approve to finalize, or flag for modification to return to analysis."
      />

      <div className="rounded-lg border border-border bg-panel p-5">
        <div className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground">
          Inspection reference
        </div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm md:grid-cols-4">
          <Ref label="Inspection ID" value={inspectionId} mono />
          <Ref label="Generated" value={new Date().toLocaleString()} />
          <Ref label="Aircraft" value="Boeing 737" />
          <Ref label="Zone" value={detection.zone} />
        </dl>
      </div>

      {analysis && !locked && (
        <div className="rounded-lg border border-border bg-panel p-5">
          <div className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground">
            Repair plan summary
          </div>
          <p className="text-sm leading-relaxed">{analysis.recommendation}</p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <MiniList title="Applicable regulations">
              {analysis.regulations.map((r) => (
                <li key={r.id} className="flex gap-2">
                  <span className="font-mono text-xs text-primary">{r.id}</span>
                  <span className="text-muted-foreground">— {r.source}</span>
                </li>
              ))}
            </MiniList>
            <MiniList title="Post-repair conditions">
              {analysis.conditions.map((c, i) => (
                <li key={i} className="flex gap-2 text-muted-foreground">
                  <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-warning" />
                  {c}
                </li>
              ))}
            </MiniList>
          </div>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <ReportCard
          icon={FileText}
          title="Defect Analysis Report"
          desc="Full detection result, regulation match, and airworthiness determination."
          report={reports.find((r) => r.type === "defect_analysis")}
          locked={locked}
          downloadable={finalized}
          inspectionId={inspectionId}
        />
        <ReportCard
          icon={ClipboardList}
          title="Work Order"
          desc="Repair scheme, parts list, and sign-off blocks per Boeing SRM 53-30."
          report={reports.find((r) => r.type === "work_order")}
          locked={locked}
          downloadable={finalized}
          inspectionId={inspectionId}
        />
      </div>

      {!locked && (
        <>
          {flagged && (
            <div className="rounded-lg border border-warning/40 bg-warning/10 p-5 text-sm">
              <div className="mb-1 flex items-center gap-2 font-semibold text-warning">
                <Flag className="h-4 w-4" />
                Flagged for modification
              </div>
              <div className="text-xs font-mono uppercase tracking-wider text-muted-foreground">
                {reportApproval.by} · {reportApproval.at && new Date(reportApproval.at).toLocaleString()}
              </div>
              <p className="mt-2 text-foreground">{reportApproval.notes}</p>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => {
                    resetReportApproval();
                    navigate({ to: "/analysis" });
                  }}
                  className="inline-flex h-9 items-center gap-2 rounded-md bg-warning px-3 text-xs font-medium text-warning-foreground hover:bg-warning/90"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Return to analysis
                </button>
                <button
                  onClick={resetReportApproval}
                  className="inline-flex h-9 items-center gap-2 rounded-md border border-border bg-background px-3 text-xs font-medium hover:bg-muted"
                >
                  Dismiss flag
                </button>
              </div>
            </div>
          )}

          {finalized && (
            <div className="rounded-md border border-success/30 bg-success/10 px-4 py-3 text-sm">
              <CheckCircle2 className="mr-2 inline h-4 w-4 text-success" />
              Repair plan approved by {reportApproval.by} on{" "}
              {reportApproval.at && new Date(reportApproval.at).toLocaleString()}. Reports are now available for download.
              {reportApproval.notes && (
                <div className="mt-1 text-muted-foreground">Notes: {reportApproval.notes}</div>
              )}
            </div>
          )}

          {reportApproval.status === "pending" && (
            <div className="rounded-lg border border-border bg-panel p-5">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                <AlertTriangle className="h-4 w-4 text-warning" />
                Inspector sign-off required
              </div>
              <p className="mb-4 text-xs text-muted-foreground">
                Reports are held pending review. Approve to unlock download, or flag for modification to send the plan back to analysis with a note.
              </p>

              {flagOpen ? (
                <div className="space-y-3">
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                    Reason for flagging
                  </label>
                  <textarea
                    value={flagReason}
                    onChange={(e) => setFlagReason(e.target.value)}
                    rows={3}
                    placeholder="e.g. Parts list missing MS20470 rivets; regulation citation FAA-AD-2021-08-12 not applicable to this MSN."
                    className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:border-primary focus:outline-none"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => {
                        setFlagOpen(false);
                        setFlagReason("");
                      }}
                      className="h-9 rounded-md border border-border bg-background px-3 text-xs font-medium hover:bg-muted"
                    >
                      Cancel
                    </button>
                    <button
                      disabled={flagReason.trim().length < 5}
                      onClick={() => {
                        flagReports(flagReason.trim());
                        setFlagOpen(false);
                        setFlagReason("");
                      }}
                      className="inline-flex h-9 items-center gap-2 rounded-md bg-warning px-3 text-xs font-medium text-warning-foreground hover:bg-warning/90 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <Flag className="h-3.5 w-3.5" />
                      Submit flag
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <label className="mb-1.5 block text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                      Approval notes (optional)
                    </label>
                    <input
                      value={approveNotes}
                      onChange={(e) => setApproveNotes(e.target.value)}
                      placeholder="e.g. Confirmed with lead engineer; parts on hand at MRO."
                      className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:border-primary focus:outline-none"
                    />
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    <button
                      onClick={() => setFlagOpen(true)}
                      className="inline-flex h-10 items-center gap-2 rounded-md border border-warning/40 bg-warning/10 px-4 text-sm font-medium text-warning hover:bg-warning/15"
                    >
                      <Flag className="h-4 w-4" />
                      Flag for modification
                    </button>
                    <button
                      onClick={() => approveReports(approveNotes.trim() || undefined)}
                      className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                    >
                      <CheckCircle2 className="h-4 w-4" />
                      Approve repair plan
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      <div className="flex justify-end border-t border-border pt-5">
        <button
          onClick={() => {
            reset();
            navigate({ to: "/inspection" });
          }}
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-medium hover:bg-muted"
        >
          <RotateCcw className="h-4 w-4" />
          Start new inspection
        </button>
      </div>
    </div>
  );
}

function Ref({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</dt>
      <dd className={"mt-0.5 " + (mono ? "font-mono text-primary" : "text-foreground")}>
        {value}
      </dd>
    </div>
  );
}

function MiniList({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1.5 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
        {title}
      </div>
      <ul className="space-y-1.5 text-sm">{children}</ul>
    </div>
  );
}

function ReportCard({
  icon: Icon,
  title,
  desc,
  report,
  locked,
  downloadable,
  inspectionId
}: {
  icon: typeof FileText;
  title: string;
  desc: string;
  report?: { id: string; type: string; name: string; createdAt: string };
  locked: boolean;
  downloadable: boolean;
  inspectionId: string | null;
}) {
  // Downloading PDF from backend report generation
  async function download() {
    if (!report || !inspectionId) return;

    try {

      const endpoint = report.type === "defect_analysis"
        ? `http://localhost:8000/api/reports/${inspectionId}/defect-report`
        : `http://localhost:8000/api/reports/${inspectionId}/work-order`;

      const res = await fetch(endpoint);

      if (!res.ok) {
        console.error("Report download failed:", res.status);
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${report.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
    }
  }

  return (
    <div
      className={
        "relative rounded-lg border bg-panel p-5 transition " +
        (locked ? "border-border opacity-60" : "border-border")
      }
    >
      <div className="flex items-start gap-4">
        <div
          className={
            "flex h-12 w-12 items-center justify-center rounded-md ring-1 " +
            (locked
              ? "bg-muted text-muted-foreground ring-border"
              : "bg-primary/15 text-primary ring-primary/30")
          }
        >
          <Icon className="h-6 w-6" />
        </div>
        <div className="flex-1 space-y-1">
          <div className="flex flex-wrap items-center gap-2 text-base font-semibold">
            {title}
            {!locked && downloadable && (
              <span className="rounded bg-success/15 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-success">
                Approved
              </span>
            )}
            {!locked && !downloadable && (
              <span className="rounded bg-warning/15 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-warning">
                Pending sign-off
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground">{desc}</p>
          {report && (
            <div className="pt-1 font-mono text-xs text-muted-foreground">{report.id}</div>
          )}
        </div>
      </div>

      <div className="mt-5 border-t border-border pt-4">
        {locked ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-4 w-4" />
            Pending approval — complete Analysis to unlock.
          </div>
        ) : downloadable ? (
          <button
            onClick={download}
            className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Download className="h-4 w-4" />
            Download PDF
          </button>
        ) : (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <X className="h-4 w-4" />
            Awaiting inspector sign-off on repair plan.
          </div>
        )}
      </div>
    </div>
  );
}
