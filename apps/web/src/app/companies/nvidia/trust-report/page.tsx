import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchNvidiaTrustReport } from "@/lib/api";

export const metadata: Metadata = {
  title: "NVIDIA Trust Report | APIP",
  description: "Full APIP trust report for NVIDIA Gold Standard validation."
};

export default async function NvidiaTrustReportPage() {
  const report = await fetchNvidiaTrustReport();
  return (
    <div className="grid gap-6">
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">NVIDIA Gold Standard</p>
        <h1 className="text-4xl font-semibold">Trust Report</h1>
        <p className="max-w-3xl text-muted-foreground">
          NVIDIA is the second APIP Gold Standard company, with evidence collected, scored,
          reviewed, approved, published, and linked to public lineage.
        </p>
        <div className="flex flex-wrap gap-2">
          {report.gold_standard_label ? <Badge>{report.gold_standard_label}</Badge> : null}
          {report.workflow.split(" -> ").map((step) => (
            <Badge key={step}>{step}</Badge>
          ))}
        </div>
      </header>
      <section className="grid gap-4 md:grid-cols-4">
        {[
          ["Total Evidence", report.metrics.total_records],
          ["Published", report.metrics.published_records],
          ["Average Confidence", report.metrics.average_confidence.toFixed(1)],
          ["Average OpenVals", report.metrics.average_openvals_score.toFixed(1)]
        ].map(([label, value]) => (
          <Card key={label}>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p>
              <CardTitle className="text-2xl tabular-nums">{value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>
      <section className="grid gap-3">
        {report.items.map((item) => (
          <Card key={item.id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle>{item.metric_name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{item.evidence_text}</p>
                </div>
                <Badge>{item.evidence_classification}</Badge>
              </div>
            </CardHeader>
            <CardContent className="grid gap-2 text-sm text-muted-foreground md:grid-cols-4">
              <span>Confidence: {item.confidence_score.toFixed(1)}</span>
              <span>Coverage: {item.evidence_coverage_score.toFixed(1)}%</span>
              <span>OpenVals: {item.openvals_score.toFixed(1)}</span>
              <span>Reviewer: {item.reviewer ?? "n/a"}</span>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
