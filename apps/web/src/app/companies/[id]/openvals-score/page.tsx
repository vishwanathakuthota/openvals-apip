import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchCompanyOpenValsScore } from "@/lib/api";

export default async function CompanyOpenValsScorePage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const score = await fetchCompanyOpenValsScore(id);

  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">
          AI Economy Validation
        </p>
        <h1 className="text-4xl font-semibold">{score.company} OpenVals Score</h1>
        <div className="flex flex-wrap gap-2">
          {score.validation_label ? <Badge>{score.validation_label}</Badge> : null}
          <Badge>{score.classification}</Badge>
        </div>
        <p className="max-w-3xl text-muted-foreground">{score.methodology_note}</p>
      </header>
      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl tabular-nums">
              {score.openvals_score.toFixed(1)}
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Progress value={score.openvals_score} />
            <p className="text-sm text-muted-foreground">
              Published records: {score.published_records}
            </p>
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
