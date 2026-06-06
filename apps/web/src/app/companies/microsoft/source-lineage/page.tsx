import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchMicrosoftSourceLineage } from "@/lib/api";

export const metadata: Metadata = {
  title: "Microsoft Source Lineage | APIP",
  description: "Source lineage for published Microsoft APIP metrics."
};

export default async function MicrosoftSourceLineagePage() {
  const lineage = await fetchMicrosoftSourceLineage();
  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Microsoft Pilot</p>
        <h1 className="text-4xl font-semibold">Source Lineage</h1>
        <p className="max-w-3xl text-muted-foreground">
          Every published Microsoft metric includes its source URL, type, collection date,
          confidence, evidence coverage, reviewer, and approval date.
        </p>
      </header>
      <section className="grid gap-4 md:grid-cols-3">
        {lineage.items.map((item) => (
          <Card key={`${item.source_url}-${item.collection_date}`}>
            <CardHeader>
              <CardTitle>{item.source_type.replaceAll("_", " ")}</CardTitle>
              <Badge>{item.evidence_classification}</Badge>
            </CardHeader>
            <CardContent className="grid gap-2 text-sm text-muted-foreground">
              <a className="text-foreground underline-offset-4 hover:underline" href={item.source_url} rel="noreferrer" target="_blank">
                Source URL
              </a>
              <span>Collected: {formatDate(item.collection_date)}</span>
              <span>Confidence: {item.confidence.toFixed(1)}</span>
              <span>Coverage: {item.evidence_coverage.toFixed(1)}%</span>
              <span>Reviewer: {item.reviewer ?? "n/a"}</span>
              <span>Approved: {formatDate(item.approval_date)}</span>
              <span>OpenVals: {item.openvals_score.toFixed(1)}</span>
            </CardContent>
          </Card>
        ))}
        {lineage.items.length === 0 ? (
          <p className="rounded-lg border border-border p-5 text-sm text-muted-foreground">
            No published Microsoft lineage records are available yet.
          </p>
        ) : null}
      </section>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(new Date(value));
}
