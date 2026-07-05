import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { Plane, LogOut, Bell, Lock } from "lucide-react";
import { useWorkflow } from "../../hooks/use_inspection";
import { useAuth } from "../../hooks/use_auths";
import { cn } from "../../lib/utils";

interface TabDef {
  to: string;
  label: string;
  locked?: boolean;
  lockReason?: string;
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { inspectionId, approvedDetection, approvedAnalysis, detection } = useWorkflow();

  const tabs: TabDef[] = [
    { to: "/inspection", label: "Inspection" },
    {
      to: "/twin",
      label: "Digital Twin",
      locked: !approvedDetection,
      lockReason: "Complete inspection first to view the digital twin",
    },
    {
      to: "/analysis",
      label: "Analysis",
      locked: !approvedDetection,
      lockReason: "Complete inspection first to access Analysis",
    },
    {
      to: "/reports",
      label: "Reports",
      locked: !approvedAnalysis,
      lockReason: "Complete analysis first to access Reports",
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-border bg-panel/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-[1400px] items-center gap-8 px-6">
          <Link to="/inspection" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 ring-1 ring-primary/40">
              <Plane className="h-5 w-5 text-primary" />
            </div>
            <div className="leading-tight">
              <div className="font-mono text-sm font-semibold tracking-wider text-foreground">
                AEROINSPECT
              </div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground">
                B737 · Inspection Suite
              </div>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            {tabs.map((t) => {
              const active = pathname.startsWith(t.to);
              if (t.locked) {
                return (
                  <span
                    key={t.to}
                    title={t.lockReason}
                    className="inline-flex cursor-not-allowed items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground/50"
                  >
                    <Lock className="h-3.5 w-3.5" />
                    {t.label}
                  </span>
                );
              }
              return (
                <Link
                  key={t.to}
                  to={t.to}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-primary/15 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  {t.label}
                </Link>
              );
            })}
          </nav>

          <div className="ml-auto flex items-center gap-3">
            <button className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
              <Bell className="h-4 w-4" />
              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-warning" />
            </button>
            {user && (
              <div className="flex items-center gap-3 border-l border-border pl-3">
                <div className="text-right leading-tight">
                  <div className="text-sm font-medium">{user.name}</div>
                  <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={() => {
                    signOut();
                    navigate({ to: "/login" });
                  }}
                  className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
                  title="Sign out"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </div>

        {inspectionId && detection && (
          <div className="border-t border-border bg-background/40">
            <div className="mx-auto flex max-w-[1400px] items-center gap-4 px-6 py-2 font-mono text-xs">
              <span className="text-muted-foreground">ACTIVE INSPECTION</span>
              <span className="text-primary">{inspectionId}</span>
              <span className="text-muted-foreground">·</span>
              <span>{detection.zone}</span>
              <span className="text-muted-foreground">·</span>
              <span>{detection.defectType}</span>
              <div className="ml-auto flex items-center gap-3 text-muted-foreground">
                <StepDot label="Detection" active done={approvedDetection} />
                <span className="text-border">›</span>
                <StepDot label="Twin" active={approvedDetection} done={approvedDetection} />
                <span className="text-border">›</span>
                <StepDot label="Analysis" active={approvedDetection} done={approvedAnalysis} />
                <span className="text-border">›</span>
                <StepDot label="Reports" active={approvedAnalysis} done={approvedAnalysis} />
              </div>
            </div>
          </div>
        )}
      </header>
      <main className="mx-auto max-w-[1400px] px-6 py-8">{children}</main>
    </div>
  );
}

function StepDot({ label, active, done }: { label: string; active?: boolean; done?: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          done ? "bg-success" : active ? "bg-primary" : "bg-border",
        )}
      />
      <span className={cn(done || active ? "text-foreground" : "text-muted-foreground")}>
        {label}
      </span>
    </span>
  );
}
