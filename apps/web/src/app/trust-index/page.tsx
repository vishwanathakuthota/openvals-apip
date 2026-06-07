import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchTrustIndex } from "@/lib/api";

export const metadata: Metadata = {
  title: "OpenVals Trust Index | APIP",
  description:
    "The primary APIP trust metric combining confidence, evidence coverage, transparency, reproducibility, and source quality."
};

export default async function TrustIndexPage() {
  const trust = await fetchTrustIndex();
  const summary = trust.summary;
  return (
    <div className="grid gap-8">
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">OpenVals Trust Index</p>
        <h1 className="text-4xl font-semibold">Primary trust metric for APIP</h1>
        <p className="max-w-3xl text-muted-foreground">{trust.methodology.formula}</p>
      </header>

      <section className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <CardTitle className="text-4xl tabular-nums">{summary.trust_index.toFixed(1)}</CardTitle>
              <Badge>{summary.trust_rating}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{summary.trust_classification}</p>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Progress value={summary.trust_index} />
            <p className="text-sm text-muted-foreground">
              {summary.published_record_count} published records · {summary.source_count} sources
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Component Scores</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {Object.entries(summary.components).map(([key, value]) => (
              <div className="grid gap-2" key={key}>
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="capitalize text-muted-foreground">{key.replaceAll("_", " ")}</span>
                  <span className="tabular-nums">{value.toFixed(1)}</span>
                </div>
                <Progress value={value} />
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Historical Trust Trend</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm text-muted-foreground">
            {trust.trend.slice(0, 8).map((item) => (
              <div className="flex items-center justify-between gap-3" key={`${item.entity_name}-${item.snapshot_date}`}>
                <span>{item.entity_name} · {item.snapshot_date}</span>
                <span className="tabular-nums">{item.trust_index.toFixed(1)}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Trust Change Notifications</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm text-muted-foreground">
            {trust.notifications.slice(0, 8).map((item) => (
              <div className="rounded-md border border-border p-3" key={item.id}>
                {item.message}
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
