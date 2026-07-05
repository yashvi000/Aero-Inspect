import type { ReactNode } from "react";

export function EmptyState({
  icon,
  title,
  children,
}: {
  icon?: ReactNode;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex h-full min-h-[300px] flex-col items-center justify-center gap-3 text-center text-muted-foreground">
      {icon}
      <div>
        <div className="text-sm font-medium text-foreground">{title}</div>
        {children && <div className="mt-1 max-w-xs text-xs">{children}</div>}
      </div>
    </div>
  );
}
