import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchTrustIndex } from "@/lib/api";

export const metadata: Metadata = {
  title: "Trust Methodology | APIP",
  description:
    "OpenVals Trust Index methodology for APIP confidence, evidence coverage, transparency, reproducibility, and source quality scoring."
};

export default async function TrustMethodologyPage() {
  const dashboard = await fetchTrustIndex();
  const methodology = dashboard.methodology;
  const summary = dashboard.summary;

  return (
    <div className="grid gap-8">
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">
          OpenVals Trust Methodology
        </p>
        <h1 className="text-4xl font-semibold">How APIP decides whether a metric can be trusted</h1>
        <p className="max-w-3xl text-muted-foreground">
          The Trust Index combines confidence, coverage, transparency, reproducibility, and
          source quality into one public score. It is calculated after evidence is approved and
          before published dashboards or APIs expose the metric.
        </p>
        <div className="flex flex-wrap gap-2">
          <Badge>{methodology.version}</Badge>
          <Badge>{summary.trust_rating}</Badge>
          <Badge>{summary.trust_classification}</Badge>
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-[1fr_1.4fr]">
        <Card>
          <CardHeader>
            <CardTitle>Current Global Trust Index</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <p className="text-5xl font-semibold tabular-nums">{summary.trust_index.toFixed(1)}</p>
            <Progress value={summary.trust_index} />
            <p className="text-sm text-muted-foreground">
              {summary.published_record_count} published records from {summary.source_count} sources.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Formula</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm text-muted-foreground">
            <p>{methodology.formula}</p>
            {Object.entries(methodology.weights).map(([label, weight]) => (
              <div className="grid gap-1" key={label}>
                <div className="flex items-center justify-between gap-3">
                  <span className="capitalize">{label.replaceAll("_", " ")}</span>
                  <span className="tabular-nums">{(weight * 100).toFixed(0)}%</span>
                </div>
                <Progress value={weight * 100} />
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {Object.entries(methodology.rating_scale).map(([range, label]) => (
          <Card key={range}>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">{range}</p>
              <CardTitle>{label}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Traceability Contract</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm text-muted-foreground md:grid-cols-3">
          <p>Every public metric must show source URL, source type, confidence, and coverage.</p>
          <p>Every published value must retain reviewer approval history and lineage metadata.</p>
          <p>
            Historical snapshots and trust notifications are available in the{" "}
            <Link className="text-foreground underline-offset-4 hover:underline" href="/trust-index">
              Trust Index
            </Link>
            .
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
