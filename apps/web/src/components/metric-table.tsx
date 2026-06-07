import { ConfidenceScore } from "@/components/confidence-score";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatMetric } from "@/lib/format";
import type { MetricValue } from "@/types/api";

export function MetricTable({ metrics }: { metrics: MetricValue[] }) {
  if (!metrics.length) {
    return (
      <EmptyState
        title="No approved metrics yet"
        message="Metrics appear after source evidence is imported, scored, and approved by an APIP administrator."
      />
    );
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
      <div className="overflow-x-auto rounded-lg border border-border">
        <div className="grid min-w-[1160px] grid-cols-[1fr_120px_130px_110px_120px_130px_130px_110px_140px] border-b border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
          <span>Metric</span>
          <span>Value</span>
          <span>Confidence</span>
          <span>Trust</span>
          <span>Coverage</span>
          <span>Class</span>
          <span>Validation</span>
          <span>Sources</span>
          <span>Updated</span>
        </div>
        {metrics.map((metric) => (
          <div
            className="grid min-w-[1160px] grid-cols-[1fr_120px_130px_110px_120px_130px_130px_110px_140px] border-b border-border px-4 py-3 text-sm"
            key={metric.id}
          >
            <span className="group relative">
              {metric.metric_key.replaceAll("_", " ")}
              <span className="pointer-events-none absolute left-0 top-7 z-20 hidden w-80 rounded-lg border border-border bg-card p-4 text-sm shadow-xl group-hover:grid">
                <strong>{metric.metric_key.replaceAll("_", " ")}</strong>
                <span className="mt-2 text-muted-foreground">
                  Value: {formatMetric(metric.value, metric.unit)}
                </span>
                <span className="text-muted-foreground">
                  Confidence: {metric.confidence_score?.toFixed(1) ?? "n/a"} ({metric.confidence_label ?? "n/a"})
                </span>
                <span className="text-muted-foreground">
                  Coverage: {metric.coverage_score?.toFixed(0) ?? "n/a"} ({metric.coverage_label ?? "n/a"})
                </span>
                <span className="text-muted-foreground">Sources: {metric.source_count ?? 0}</span>
                <span className="text-muted-foreground">
                  Classification: {metric.evidence_classification ?? "n/a"}
                </span>
                <span className="text-muted-foreground">
                  Validation status: {metric.validation_status ?? "n/a"}
                </span>
                <span className="text-muted-foreground">
                  OpenVals Score: {metric.openvals_score?.toFixed(1) ?? "n/a"}
                </span>
                <span className="text-muted-foreground">
                  Trust Index: {metric.trust_index?.toFixed(1) ?? "n/a"} (
                  {metric.trust_rating ?? "n/a"})
                </span>
                <span className="text-muted-foreground">Last updated: {formatDate(metric.last_updated)}</span>
              </span>
            </span>
            <strong>{formatMetric(metric.value, metric.unit)}</strong>
            <Badge>{metric.confidence_label ?? metric.confidence?.label ?? "n/a"}</Badge>
            <Badge>{metric.trust_index?.toFixed(1) ?? "n/a"}</Badge>
            <Badge>{metric.coverage_label ?? "n/a"}</Badge>
            <Badge>{metric.evidence_classification ?? "n/a"}</Badge>
            <Badge>{metric.validation_status ?? "n/a"}</Badge>
            <span>{metric.source_count ?? metric.confidence?.source_count ?? 0}</span>
            <span>{formatDate(metric.last_updated ?? metric.confidence?.last_updated)}</span>
          </div>
        ))}
      </div>
      <div className="grid gap-4">
        <ConfidenceScore confidence={metrics[0]?.confidence ?? null} />
        <SourceTransparencyPanel metric={metrics[0]} />
      </div>
    </div>
  );
}

function SourceTransparencyPanel({ metric }: { metric?: MetricValue }) {
  if (!metric) {
    return null;
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>Source Transparency</CardTitle>
        <p className="text-sm text-muted-foreground">{metric.methodology_note ?? metric.methodology}</p>
      </CardHeader>
      <CardContent className="grid gap-3">
        {(metric.sources ?? []).map((source) => (
          <div className="grid gap-1 rounded-md border border-border p-3" key={source.id}>
            <div className="flex items-start justify-between gap-3">
              <strong className="text-sm">{source.title}</strong>
              <Badge>{source.credibility_score ?? source.reliability_score}</Badge>
            </div>
            <span className="text-xs text-muted-foreground">
              Tier {source.source_tier ?? "n/a"} · {source.source_type.replaceAll("_", " ")}
            </span>
            <span className="text-xs text-muted-foreground">{source.publisher}</span>
            <span className="text-xs text-muted-foreground">{formatDate(source.published_at)}</span>
            {source.lineage ? (
              <div className="mt-2 grid gap-1 border-t border-border pt-2 text-xs text-muted-foreground">
                <span>Collection date: {formatDate(source.lineage.collection_date)}</span>
                <span>Evidence coverage: {source.lineage.evidence_coverage.toFixed(1)}%</span>
                <span>Reviewer: {source.lineage.reviewer ?? "n/a"}</span>
                <span>Approval date: {formatDate(source.lineage.approval_date)}</span>
              </div>
            ) : null}
          </div>
        ))}
      </CardContent>
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
