import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchAlphabetTrustReport } from "@/lib/api";

export const metadata: Metadata = {
  title: "Alphabet Trust Report | APIP",
  description: "Full APIP trust report for Alphabet Gold Standard validation."
};

export default async function AlphabetTrustReportPage() {
  const report = await fetchAlphabetTrustReport();
  return (
    <div className="grid gap-6">
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Alphabet Gold Standard</p>
        <h1 className="text-4xl font-semibold">Trust Report</h1>
        <p className="max-w-3xl text-muted-foreground">
          Alphabet is the third APIP Gold Standard company, with evidence collected, scored,
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
    </div>
  );
}
