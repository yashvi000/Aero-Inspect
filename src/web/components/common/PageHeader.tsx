export function PageHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="space-y-1.5">
      <div className="font-mono text-xs uppercase tracking-[0.2em] text-primary">{eyebrow}</div>
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      {subtitle && <p className="max-w-2xl text-sm text-muted-foreground">{subtitle}</p>}
    </div>
  );
}
