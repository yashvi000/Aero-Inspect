import { useState, useRef } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Upload, Loader2, CheckCircle2, XCircle, ImageIcon } from "lucide-react";
import { useWorkflow } from "../../hooks/use_inspection";
import type { DetectionResult, Severity } from "../../types";
import { INSPECTION_TYPES, DEFECT_TYPES } from "../../lib/constants";
import { useZones } from "../../hooks/use_zones";
import { PageHeader } from "../../components/common/PageHeader";
import { EmptyState } from "../../components/feedback/EmptyState";

export function InspectionPage() {
  const navigate = useNavigate();
  const { detection, setDetection, approveDetection, rejectDetection, approvedDetection } =
    useWorkflow();
  const zones = useZones();

  const [inspType, setInspType] = useState(INSPECTION_TYPES[0]);
  const [zone, setZone] = useState(zones[2]);
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(f: File | null) {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!preview) return;
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1400));
    const defect = DEFECT_TYPES[Math.floor(Math.random() * DEFECT_TYPES.length)];
    const conf = 0.78 + Math.random() * 0.2;
    const sev: Severity = conf > 0.92 ? "High" : conf > 0.85 ? "Medium" : "Low";
    const det: DetectionResult = {
      imageUrl: preview,
      defectType: defect,
      confidence: conf,
      severity: sev,
      zone,
      bbox: { x: 0.32, y: 0.28, w: 0.32, h: 0.28 },
    };
    setDetection(det);
    setLoading(false);
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Step 01 / 04"
        title="Inspection"
        subtitle="Upload zone imagery for AI-assisted defect detection. Approve to unlock the digital twin and airworthiness analysis."
      />

      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <form
          onSubmit={onSubmit}
          className="space-y-5 rounded-lg border border-border bg-panel p-5"
        >
          <SectionTitle>Inspection parameters</SectionTitle>

          <ReadOnlyField label="Aircraft type" value="Boeing 737" />

          <SelectField
            label="Inspection type"
            value={inspType}
            onChange={setInspType}
            options={INSPECTION_TYPES}
          />

          <SelectField label="Zone" value={zone} onChange={setZone} options={zones} />

          <label className="block space-y-1.5">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Description <span className="lowercase text-muted-foreground/60">(optional)</span>
            </span>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Observed conditions, lighting, prior repairs…"
              className="block w-full rounded-md border border-input bg-input/40 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/30"
            />
          </label>

          <div className="space-y-1.5">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Image upload
            </span>
            <div
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                handleFile(e.dataTransfer.files?.[0] ?? null);
              }}
              className="flex h-40 cursor-pointer flex-col items-center justify-center gap-2 rounded-md border-2 border-dashed border-border bg-background/40 text-center text-muted-foreground transition hover:border-primary hover:text-primary"
            >
              {file ? (
                <>
                  <ImageIcon className="h-6 w-6" />
                  <div className="text-sm">{file.name}</div>
                  <div className="text-xs text-muted-foreground">Click to replace</div>
                </>
              ) : (
                <>
                  <Upload className="h-6 w-6" />
                  <div className="text-sm font-medium">Drag &amp; drop image</div>
                  <div className="text-xs">or click to browse · JPG / PNG up to 10MB</div>
                </>
              )}
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:opacity-50"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading ? "Analyzing image…" : "Run detection"}
          </button>
        </form>

        <div className="rounded-lg border border-border bg-panel p-5">
          {loading ? (
            <LoadingState />
          ) : detection ? (
            <ResultPanel
              onApprove={() => {
                approveDetection();
                navigate({ to: "/twin" });
              }}
              onReject={rejectDetection}
              approved={approvedDetection}
              onContinue={() => navigate({ to: "/twin" })}
            />
          ) : (
            <EmptyState
              icon={<ImageIcon className="h-10 w-10 opacity-40" />}
              title="No detection yet"
            >
              Fill the inspection form and upload an image to run the defect detection model.
            </EmptyState>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultPanel({
  onApprove,
  onReject,
  approved,
  onContinue,
}: {
  onApprove: () => void;
  onReject: () => void;
  approved: boolean;
  onContinue: () => void;
}) {
  const { detection } = useWorkflow();
  if (!detection) return null;
  const sevColor =
    detection.severity === "High"
      ? "text-critical bg-critical/10 ring-critical/30"
      : detection.severity === "Medium"
        ? "text-warning bg-warning/10 ring-warning/30"
        : "text-success bg-success/10 ring-success/30";

  return (
    <div className="space-y-5">
      <div className="flex items-baseline justify-between">
        <SectionTitle>Detection result</SectionTitle>
        <span className="font-mono text-xs text-muted-foreground">
          model · yolov8-airframe-v3
        </span>
      </div>

      <div className="relative overflow-hidden rounded-md border border-border bg-background">
        <img
          src={detection.imageUrl}
          alt="Inspection"
          className="block max-h-[420px] w-full object-contain"
        />
        <div
          className="pointer-events-none absolute border-2 border-primary shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]"
          style={{
            left: `${detection.bbox.x * 100}%`,
            top: `${detection.bbox.y * 100}%`,
            width: `${detection.bbox.w * 100}%`,
            height: `${detection.bbox.h * 100}%`,
          }}
        >
          <div className="absolute -top-6 left-0 rounded-sm bg-primary px-1.5 py-0.5 font-mono text-[10px] font-semibold text-primary-foreground">
            {detection.defectType} · {(detection.confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3 text-sm">
        <Stat label="Defect" value={detection.defectType} />
        <Stat label="Confidence" value={`${(detection.confidence * 100).toFixed(1)}%`} />
        <Stat
          label="Severity"
          value={
            <span className={`inline-flex rounded px-1.5 py-0.5 text-xs font-medium ring-1 ${sevColor}`}>
              {detection.severity}
            </span>
          }
        />
        <Stat label="Zone" value={detection.zone.split(" — ")[0]} />
      </div>

      {approved ? (
        <div className="flex items-center justify-between rounded-md border border-success/30 bg-success/10 px-4 py-3">
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle2 className="h-4 w-4 text-success" />
            <span>Detection approved &mdash; ready to view digital twin.</span>
          </div>
          <button
            onClick={onContinue}
            className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
          >
            Continue to Digital Twin →
          </button>
        </div>
      ) : (
        <div className="flex gap-3">
          <button
            onClick={onApprove}
            className="inline-flex h-10 flex-1 items-center justify-center gap-2 rounded-md bg-success px-4 text-sm font-medium text-success-foreground hover:bg-success/90"
          >
            <CheckCircle2 className="h-4 w-4" />
            Approve &amp; investigate
          </button>
          <button
            onClick={onReject}
            className="inline-flex h-10 flex-1 items-center justify-center gap-2 rounded-md border border-border bg-background text-sm font-medium hover:bg-muted"
          >
            <XCircle className="h-4 w-4" />
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex h-full min-h-[420px] flex-col items-center justify-center gap-4 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <div>
        <div className="text-sm font-medium">Analyzing image…</div>
        <div className="mt-1 font-mono text-xs text-muted-foreground">
          preprocessing → inference → postprocess
        </div>
      </div>
      <div className="h-1 w-64 overflow-hidden rounded-full bg-muted">
        <div className="h-full w-1/2 animate-pulse rounded-full bg-primary" />
      </div>
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground">
      {children}
    </div>
  );
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1.5">
      <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <div className="flex h-10 items-center justify-between rounded-md border border-input bg-background/40 px-3 text-sm">
        <span>{value}</span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          fixed
        </span>
      </div>
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block h-10 w-full rounded-md border border-input bg-input/40 px-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/30"
      >
        {options.map((o) => (
          <option key={o} value={o} className="bg-panel">
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border border-border bg-background/40 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-0.5 text-sm font-medium">{value}</div>
    </div>
  );
}
