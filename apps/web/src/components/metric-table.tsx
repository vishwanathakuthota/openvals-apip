import { ConfidenceScore } from "@/components/confidence-score";
import { formatMetric } from "@/lib/format";
import type { MetricValue } from "@/types/api";

export function MetricTable({ metrics }: { metrics: MetricValue[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
      <div className="overflow-hidden rounded-lg border border-border">
        <div className="grid grid-cols-[1fr_120px_120px] border-b border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
          <span>Metric</span>
          <span>Value</span>
          <span>Confidence</span>
        </div>
        {metrics.map((metric) => (
          <div className="grid grid-cols-[1fr_120px_120px] border-b border-border px-4 py-3 text-sm" key={metric.id}>
            <span>{metric.metric_key.replaceAll("_", " ")}</span>
            <strong>{formatMetric(metric.value, metric.unit)}</strong>
            <span>{metric.confidence?.label ?? "n/a"}</span>
          </div>
        ))}
      </div>
      <ConfidenceScore confidence={metrics[0]?.confidence ?? null} />
    </div>
  );
}
