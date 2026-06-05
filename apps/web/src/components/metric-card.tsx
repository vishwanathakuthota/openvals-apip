import { formatMetric } from "@/lib/format";
import type { Confidence } from "@/types/api";

import { Card, CardContent } from "./ui/card";

export function MetricCard({
  label,
  value,
  unit,
  confidence
}: {
  label: string;
  value: number;
  unit: string;
  confidence: Confidence;
}) {
  return (
    <Card className="group relative">
      <CardContent className="grid gap-3 p-5">
        <div className="flex items-start justify-between gap-3">
          <span className="text-sm text-muted-foreground">{label}</span>
          <span className="rounded-sm border border-primary/40 px-2 py-1 text-xs text-primary">
            {confidence.score.toFixed(1)}
          </span>
        </div>
        <strong className="text-2xl">{formatMetric(value, unit)}</strong>
        <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
          <span>{confidence.source_count} sources</span>
          <span>{formatDate(confidence.last_updated)}</span>
        </div>
      </CardContent>
      <div className="pointer-events-none absolute left-4 top-[calc(100%-8px)] z-30 hidden w-72 rounded-lg border border-border bg-card p-4 text-sm shadow-xl group-hover:grid">
        <strong>{label}</strong>
        <span className="mt-2 text-muted-foreground">Value: {formatMetric(value, unit)}</span>
        <span className="text-muted-foreground">
          Confidence: {confidence.score.toFixed(1)} ({confidence.label})
        </span>
        <span className="text-muted-foreground">Sources: {confidence.source_count}</span>
        <span className="text-muted-foreground">Last updated: {formatDate(confidence.last_updated)}</span>
      </div>
    </Card>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(
    new Date(value)
  );
}
