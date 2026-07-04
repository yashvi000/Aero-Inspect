import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  CheckCircle2,
  AlertTriangle,
  OctagonAlert,
  Loader2,
  Edit3,
  ShieldAlert,
  RotateCcw,
  X,
} from "lucide-react";
import { useWorkflow } from "../../hooks/use_inspection";
import type {
  AnalysisResult,
  Airworthiness,
  AirworthinessOverride,
} from "../../types";
import { PageHeader } from "../../components/common/PageHeader";

const NODES = [
  "Retrieving documents",
  "Matching regulations",
  "Assessing airworthiness",
  "Generating repair plan",
];

export function AnalysisPage() {
  const navigate = useNavigate();
  const {
    detection,
    analysis,
    setAnalysis,
    approveAnalysis,
    approvedAnalysis,
    airworthinessOverride,
    overrideAirworthiness,
    clearAirworthinessOverride,
  } = useWorkflow();
  const [activeNode, setActiveNode] = useState(0);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!detection || analysis) return;
    setRunning(true);
    setActiveNode(0);
    const interval = setInterval(() => {
      setActiveNode((n) => {
        if (n >= NODES.length - 1) {
          clearInterval(interval);
          setRunning(false);
          setAnalysis(buildMockAnalysis(detection.severity, detection.defectType, detection.zone));
          return n;
        }
        return n + 1;
      });
    }, 700);
    return () => clearInterval(interval);
  }, [detection, analysis, setAnalysis]);

  if (!detection) {
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
        eyebrow="Step 03 / 04"
        title="Airworthiness Analysis"
        subtitle="Agent-driven regulation matching and airworthiness determination. Review and approve to generate compliance reports."
      />

      {running || !analysis ? (
        <AgentRunning activeNode={activeNode} />
      ) : (
        <AnalysisView
          analysis={analysis}
          approved={approvedAnalysis}
          override={airworthinessOverride}
          onOverride={overrideAirworthiness}
          onClearOverride={clearAirworthinessOverride}
          onApprove={() => {
            approveAnalysis();
            navigate({ to: "/reports" });
          }}
        />
      )}
    </div>
  );
}

function AgentRunning({ activeNode }: { activeNode: number }) {
  return (
    <div className="rounded-lg border border-border bg-panel p-10">
      <div className="mx-auto max-w-md space-y-6 text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <div>
          <div className="text-sm font-medium">Investigation agent running…</div>
          <div className="mt-1 font-mono text-xs text-muted-foreground">
            multi-step retrieval over DGCA · FAA · ASRS · SDR corpora
          </div>
        </div>
        <ul className="space-y-2.5 text-left">
          {NODES.map((n, i) => {
            const done = i < activeNode;
            const active = i === activeNode;
            return (
              <li key={n} className="flex items-center gap-3 text-sm">
                <span
                  className={
                    "flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-mono " +
                    (done
                      ? "bg-success/20 text-success"
                      : active
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground")
                  }
                >
                  {done ? "✓" : i + 1}
                </span>
                <span className={done || active ? "text-foreground" : "text-muted-foreground"}>
                  {n}
                  {active && <span className="ml-1.5 animate-pulse">…</span>}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

function AnalysisView({
  analysis,
  approved,
  override,
  onOverride,
  onClearOverride,
  onApprove,
}: {
  analysis: AnalysisResult;
  approved: boolean;
  override: AirworthinessOverride | null;
  onOverride: (status: Airworthiness, reason: string) => void;
  onClearOverride: () => void;
  onApprove: () => void;
}) {
  const [overrideOpen, setOverrideOpen] = useState(false);
  return (
    <div className="space-y-6">
      <StatusBanner status={analysis.airworthiness} override={override} />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Probable causes">
          <ul className="space-y-2 text-sm">
            {analysis.probableCauses.map((c, i) => (
              <li key={i} className="flex gap-2">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Airworthiness detail">
          <ul className="space-y-2 text-sm">
            {analysis.conditions.map((c, i) => (
              <li key={i} className="flex gap-2">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-warning" />
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Applicable regulations" className="lg:col-span-2">
          <div className="overflow-hidden rounded-md border border-border">
            <table className="w-full text-sm">
              <thead className="bg-background/40 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-3 py-2">Regulation ID</th>
                  <th className="px-3 py-2">Source</th>
                  <th className="px-3 py-2">Requirement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {analysis.regulations.map((r) => (
                  <tr key={r.id}>
                    <td className="px-3 py-2 font-mono text-primary">{r.id}</td>
                    <td className="px-3 py-2">{r.source}</td>
                    <td className="px-3 py-2 text-muted-foreground">{r.requirement}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Similar past cases">
          <ul className="space-y-3 text-sm">
            {analysis.similarCases.map((c, i) => (
              <li key={i} className="space-y-0.5">
                <div className="font-mono text-xs text-primary">{c.ref}</div>
                <div className="text-muted-foreground">{c.summary}</div>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Recommended action">
          <p className="text-sm leading-relaxed text-foreground">{analysis.recommendation}</p>
        </Card>
      </div>

      {overrideOpen && !approved && (
        <OverrideForm
          current={analysis.airworthiness}
          onCancel={() => setOverrideOpen(false)}
          onSubmit={(status, reason) => {
            onOverride(status, reason);
            setOverrideOpen(false);
          }}
        />
      )}

      {approved ? (
        <div className="rounded-md border border-success/30 bg-success/10 px-4 py-3 text-sm">
          <CheckCircle2 className="mr-2 inline h-4 w-4 text-success" />
          Analysis approved{override ? " (with inspector override)" : ""}. Reports tab is now unlocked.
        </div>
      ) : (
        <div className="flex flex-wrap justify-end gap-3 border-t border-border pt-5">
          {override && (
            <button
              onClick={onClearOverride}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-medium hover:bg-muted"
            >
              <RotateCcw className="h-4 w-4" />
              Revert to agent status
            </button>
          )}
          <button
            onClick={() => setOverrideOpen((v) => !v)}
            className="inline-flex h-10 items-center gap-2 rounded-md border border-warning/40 bg-warning/10 px-4 text-sm font-medium text-warning hover:bg-warning/15"
          >
            <ShieldAlert className="h-4 w-4" />
            {overrideOpen ? "Cancel override" : "Override determination"}
          </button>
          <button className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-medium hover:bg-muted">
            <Edit3 className="h-4 w-4" />
            Modify findings
          </button>
          <button
            onClick={onApprove}
            className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <CheckCircle2 className="h-4 w-4" />
            Approve &amp; generate reports
          </button>
        </div>
      )}
    </div>
  );
}

function OverrideForm({
  current,
  onSubmit,
  onCancel,
}: {
  current: Airworthiness;
  onSubmit: (status: Airworthiness, reason: string) => void;
  onCancel: () => void;
}) {
  const [status, setStatus] = useState<Airworthiness>(current);
  const [reason, setReason] = useState("");
  const options: { value: Airworthiness; label: string }[] = [
    { value: "AIRWORTHY", label: "Airworthy" },
    { value: "AIRWORTHY_WITH_CONDITIONS", label: "Airworthy with conditions" },
    { value: "GROUND_AIRCRAFT", label: "Ground aircraft" },
  ];
  const canSubmit = reason.trim().length >= 5 && status !== current;
  return (
    <div className="rounded-lg border border-warning/40 bg-warning/5 p-5">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-warning">
          <ShieldAlert className="h-4 w-4" />
          Inspector override — airworthiness determination
        </div>
        <button
          onClick={onCancel}
          className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label="Close override form"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <p className="mb-4 text-xs text-muted-foreground">
        Overrides are logged against your credential and attached to the compliance record. A written justification is required.
      </p>
      <div className="space-y-3">
        <div>
          <div className="mb-1.5 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
            New determination
          </div>
          <div className="flex flex-wrap gap-2">
            {options.map((o) => (
              <button
                key={o.value}
                onClick={() => setStatus(o.value)}
                className={
                  "rounded-md border px-3 py-1.5 text-xs font-medium transition " +
                  (status === o.value
                    ? "border-primary bg-primary/15 text-primary"
                    : "border-border bg-background hover:bg-muted")
                }
              >
                {o.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="mb-1.5 block text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
            Justification
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            placeholder="e.g. Physical inspection confirmed defect exceeds SRM 53-30 allowable limits; agent underestimated severity."
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:border-primary focus:outline-none"
          />
        </div>
        <div className="flex justify-end gap-2 pt-1">
          <button
            onClick={onCancel}
            className="h-9 rounded-md border border-border bg-background px-3 text-xs font-medium hover:bg-muted"
          >
            Cancel
          </button>
          <button
            disabled={!canSubmit}
            onClick={() => onSubmit(status, reason.trim())}
            className="h-9 rounded-md bg-warning px-3 text-xs font-medium text-warning-foreground hover:bg-warning/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Apply override
          </button>
        </div>
      </div>
    </div>
  );
}

function StatusBanner({
  status,
  override,
}: {
  status: Airworthiness;
  override?: AirworthinessOverride | null;
}) {
  const config = {
    AIRWORTHY: {
      label: "AIRWORTHY",
      sub: "Aircraft cleared for continued operation",
      Icon: CheckCircle2,
      cls: "bg-success/10 border-success/40 text-success",
    },
    AIRWORTHY_WITH_CONDITIONS: {
      label: "AIRWORTHY WITH CONDITIONS",
      sub: "Continued operation permitted subject to inspection limits",
      Icon: AlertTriangle,
      cls: "bg-warning/10 border-warning/40 text-warning",
    },
    GROUND_AIRCRAFT: {
      label: "GROUND AIRCRAFT",
      sub: "Defect exceeds airworthiness limits — aircraft must be grounded",
      Icon: OctagonAlert,
      cls: "bg-critical/10 border-critical/40 text-critical",
    },
  }[status];

  const { Icon } = config;
  return (
    <div className={`space-y-3 rounded-lg border p-5 ${config.cls}`}>
      <div className="flex items-center gap-5">
        <Icon className="h-10 w-10 shrink-0" />
        <div className="flex-1">
          <div className="text-xs font-mono uppercase tracking-[0.2em] opacity-80">
            Determination
            {override && (
              <span className="ml-2 rounded bg-background/40 px-1.5 py-0.5 text-[10px]">
                Inspector override
              </span>
            )}
          </div>
          <div className="text-2xl font-bold tracking-tight">{config.label}</div>
          <div className="mt-0.5 text-sm opacity-90">{config.sub}</div>
        </div>
      </div>
      {override && (
        <div className="rounded-md border border-current/20 bg-background/30 p-3 text-xs">
          <div className="font-mono uppercase tracking-wider opacity-80">
            Override reason · {override.by} · {new Date(override.at).toLocaleString()}
          </div>
          <div className="mt-1 opacity-90">
            Original agent determination:{" "}
            <span className="font-semibold">{override.original.replaceAll("_", " ")}</span>
          </div>
          <div className="mt-1 opacity-90">{override.reason}</div>
        </div>
      )}
    </div>
  );
}

function Card({
  title,
  className = "",
  children,
}: {
  title: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={`rounded-lg border border-border bg-panel p-5 ${className}`}>
      <div className="mb-3 text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground">
        {title}
      </div>
      {children}
    </div>
  );
}

function buildMockAnalysis(
  severity: string,
  defect: string,
  zone: string,
): AnalysisResult {
  const airworthiness: Airworthiness =
    severity === "High"
      ? "GROUND_AIRCRAFT"
      : severity === "Medium"
        ? "AIRWORTHY_WITH_CONDITIONS"
        : "AIRWORTHY";

  return {
    airworthiness,
    probableCauses: [
      `Cyclic fatigue stress at ${zone.split(" — ")[1] ?? "fuselage panel"}`,
      `Environmental exposure consistent with ${defect.toLowerCase()} progression`,
      "Possible deviation from prior repair scheme (per maintenance log)",
    ],
    regulations: [
      {
        id: "DGCA-AD-2023-14",
        source: "DGCA India",
        requirement: `Repetitive ${defect.toLowerCase()} inspection of B737 ${zone.split(" — ")[0]} every 200 FC`,
      },
      {
        id: "FAA-AD-2021-08-12",
        source: "FAA",
        requirement: "Fuselage skin inspection — eddy-current required if visual indication > 0.5in",
      },
      {
        id: "B737-SRM-53-30-01",
        source: "Boeing SRM",
        requirement: "Allowable damage limits for fuselage skin panels in Section 53-30",
      },
    ],
    conditions:
      airworthiness === "AIRWORTHY"
        ? ["No restrictions. Standard inspection interval applies."]
        : [
            "Reinspect within 200 flight cycles",
            "Limit operations to non-pressurized cruise altitudes if defect grows",
            "Log finding in aircraft technical record (ATR)",
          ],
    similarCases: [
      {
        ref: "ASRS #1734221",
        summary: `Similar ${defect.toLowerCase()} on B737-800 ${zone.split(" — ")[0]} resolved via doubler repair per SRM 53-30.`,
      },
      {
        ref: "FAA SDR 2024-04781",
        summary: "Comparable finding in pre-flight inspection led to AOG and 3-day grounding for repair.",
      },
    ],
    recommendation:
      airworthiness === "GROUND_AIRCRAFT"
        ? `Ground aircraft immediately. Open work order for ${defect.toLowerCase()} repair at ${zone.split(" — ")[1]} per Boeing SRM 53-30 and reference DGCA AD 2023-14. Aircraft not to be returned to service until repair sign-off by certified engineer.`
        : `Continue operation under condition. Schedule ${defect.toLowerCase()} reinspection within 200 flight cycles. If defect grows beyond allowable damage limit, ground aircraft and initiate repair per Boeing SRM 53-30.`,
  };
}
