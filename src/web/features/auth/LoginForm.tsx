import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Plane, Loader2 } from "lucide-react";
import { useAuth } from "../../hooks/use_auths";
import { Field } from "../../components/forms/Field";

export function LoginForm() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("inspector@aeroinspect.io");
  const [password, setPassword] = useState("demo1234");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signIn(email, password);
      navigate({ to: "/inspection" });
    } catch {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden grid-bg lg:block">
        <div className="absolute inset-0 bg-gradient-to-br from-background/40 via-background/60 to-background" />
        <div className="relative flex h-full flex-col justify-between p-12">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/15 ring-1 ring-primary/40">
              <Plane className="h-5 w-5 text-primary" />
            </div>
            <div className="font-mono text-sm font-semibold tracking-wider">AEROINSPECT</div>
          </div>
          <div className="space-y-3">
            <div className="font-mono text-xs uppercase tracking-[0.3em] text-primary">
              Boeing 737 · Inspection Suite
            </div>
            <h1 className="text-4xl font-semibold tracking-tight">
              AI-assisted airframe<br />inspection &amp; airworthiness review.
            </h1>
            <p className="max-w-md text-sm text-muted-foreground">
              Upload zone imagery, get defect detection with bounding boxes,
              review agent-driven regulation analysis, and generate compliant
              work orders — all with human-in-the-loop approval.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4 border-t border-border pt-6 font-mono text-xs">
            <div>
              <div className="text-2xl text-primary">15</div>
              <div className="text-muted-foreground">Zones</div>
            </div>
            <div>
              <div className="text-2xl text-primary">5</div>
              <div className="text-muted-foreground">Defect classes</div>
            </div>
            <div>
              <div className="text-2xl text-primary">3</div>
              <div className="text-muted-foreground">Inspection types</div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center p-8">
        <form onSubmit={onSubmit} className="w-full max-w-sm space-y-6">
          <div className="space-y-1.5">
            <div className="font-mono text-xs uppercase tracking-[0.2em] text-primary">
              Sign in
            </div>
            <h2 className="text-2xl font-semibold tracking-tight">Access your console</h2>
            <p className="text-sm text-muted-foreground">
              Use your inspector credentials. Demo values are prefilled.
            </p>
          </div>

          <div className="space-y-3">
            <Field
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              autoComplete="email"
              required
            />
            <Field
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive-foreground">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:opacity-60"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {loading ? "Signing in…" : "Sign in to console"}
          </button>

          <div className="text-center text-xs text-muted-foreground">
            Protected workspace · session-bound · audit-logged
          </div>
        </form>
      </div>
    </div>
  );
}
