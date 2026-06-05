import { cn } from "@/lib/utils";

export function Progress({ value, className }: { value: number; className?: string }) {
  return (
    <div className={cn("h-2 overflow-hidden rounded-sm bg-muted", className)}>
      <div className="h-full bg-primary" style={{ width: `${Math.max(0, Math.min(value, 100))}%` }} />
    </div>
  );
}
