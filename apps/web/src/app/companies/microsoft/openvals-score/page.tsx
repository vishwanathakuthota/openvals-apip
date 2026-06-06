import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchMicrosoftOpenValsScore } from "@/lib/api";

export const metadata: Metadata = {
  title: "Microsoft OpenVals Score | APIP",
  description: "Microsoft company-level OpenVals Score from the end-to-end validation pilot."
};

export default async function MicrosoftOpenValsScorePage() {
  const score = await fetchMicrosoftOpenValsScore();
  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Microsoft Pilot</p>
        <h1 className="text-4xl font-semibold">OpenVals Score</h1>
        <p className="max-w-3xl text-muted-foreground">{score.methodology_note}</p>
      </header>
      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <CardTitle className="text-3xl tabular-nums">{score.openvals_score.toFixed(1)}</CardTitle>
              <Badge>{score.classification}</Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Progress value={score.openvals_score} />
            <p className="text-sm text-muted-foreground">Published records: {score.published_records}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Score Inputs</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm text-muted-foreground">
            <span>Confidence: {score.confidence_score.toFixed(1)}</span>
            <span>Evidence Coverage: {score.evidence_coverage_score.toFixed(1)}%</span>
            <span>Sources: {score.source_count}</span>
            <span>Last Updated: {formatDate(score.last_updated)}</span>
          </CardContent>
        </Card>
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
