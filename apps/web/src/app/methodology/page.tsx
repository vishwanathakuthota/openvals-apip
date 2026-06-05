import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "How OpenVals APIP calculates profitability metrics, confidence scores, source transparency, and the AI Reality Index."
};

const confidenceInputs = [
  ["Source Reliability", "40%", "Weights audited evidence such as SEC filings and annual reports above estimates."],
  ["Data Freshness", "20%", "Rewards recent sources and reduces stale metric confidence over time."],
  ["Cross Verification", "25%", "Increases confidence when independent sources agree on the same metric."],
  ["Methodology Transparency", "15%", "Scores whether the calculation path and assumptions are documented."]
];

const indexInputs = [
  ["ROI", "40%"],
  ["Revenue Growth", "30%"],
  ["Margin", "20%"],
  ["Adoption", "10%"]
];

export default function MethodologyPage() {
  return (
    <>
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">OpenVals Methodology</p>
        <h1 className="max-w-3xl text-4xl font-semibold">Transparent scoring for AI profitability claims</h1>
        <p className="max-w-3xl leading-7 text-muted-foreground">
          APIP separates economic outcomes from market narratives by pairing every metric with evidence, source
          lineage, confidence scoring, and reproducible formulas.
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Confidence Score Engine</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {confidenceInputs.map(([label, weight, note]) => (
              <div className="grid gap-1 rounded-md border border-border p-3" key={label}>
                <div className="flex items-center justify-between gap-3">
                  <strong>{label}</strong>
                  <Badge>{weight}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{note}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Reality Index</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <p className="rounded-md border border-border bg-muted/30 p-3 text-sm text-muted-foreground">
              AI Reality Index = ROI x 0.4 + Revenue Growth x 0.3 + Margin x 0.2 + Adoption x 0.1
            </p>
            {indexInputs.map(([label, weight]) => (
              <div className="flex items-center justify-between border-b border-border pb-2 last:border-0" key={label}>
                <span>{label}</span>
                <Badge>{weight}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </>
  );
}
