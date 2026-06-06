import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchTrustCenter } from "@/lib/api";

export const metadata: Metadata = {
  title: "OpenVals Trust Center | APIP",
  description:
    "Trace APIP evidence from collection through validation, human review, approval, and publication."
};

export default async function TrustCenterPage() {
  const trustCenter = await fetchTrustCenter();
  const metrics = [
    ["Evidence Records", trustCenter.metrics.total_records],
    ["Under Review", trustCenter.metrics.under_review_records],
    ["Published", trustCenter.metrics.published_records],
    ["Manual Review", trustCenter.metrics.manual_review_required]
  ];

  return (
    <div className="grid gap-8">
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">OpenVals Trust Center</p>
        <h1 className="text-4xl font-semibold">Every number must earn its way into APIP</h1>
        <p className="max-w-3xl text-muted-foreground">
          APIP collects evidence from approved sources, scores it, queues it for human review,
          and only publishes records after approval. Newly collected information is never
          automatically published.
        </p>
        <div className="flex flex-wrap gap-2">
          {trustCenter.workflow.split(" -> ").map((step) => (
            <Badge key={step}>{step}</Badge>
          ))}
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        {metrics.map(([label, value]) => (
          <Card key={label}>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p>
              <CardTitle className="text-2xl tabular-nums">{value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Average Confidence</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Progress value={trustCenter.metrics.average_confidence} />
            <p className="text-sm tabular-nums text-muted-foreground">
              {trustCenter.metrics.average_confidence.toFixed(1)} / 100
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Average OpenVals Score</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Progress value={trustCenter.metrics.average_openvals_score} />
            <p className="text-sm tabular-nums text-muted-foreground">
              {trustCenter.metrics.average_openvals_score.toFixed(1)} / 100
            </p>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Evidence Timeline</p>
          <h2 className="text-2xl font-semibold">Research and validation records</h2>
        </div>
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="border-b border-border text-xs uppercase text-muted-foreground">
              <tr>
                <th className="p-3">Company</th>
                <th className="p-3">Metric</th>
                <th className="p-3">Classification</th>
                <th className="p-3">Status</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Coverage</th>
                <th className="p-3">OpenVals</th>
                <th className="p-3">Source</th>
              </tr>
            </thead>
            <tbody>
              {trustCenter.items.map((item) => (
                <tr key={item.id} className="border-b border-border/70">
                  <td className="p-3 font-medium">{item.company}</td>
                  <td className="p-3">{item.metric}</td>
                  <td className="p-3">
                    <Badge>{item.evidence_classification}</Badge>
                  </td>
                  <td className="p-3">{item.status}</td>
                  <td className="p-3 tabular-nums">{item.confidence_score.toFixed(1)}</td>
                  <td className="p-3 tabular-nums">{item.evidence_coverage_score.toFixed(1)}%</td>
                  <td className="p-3 tabular-nums">{item.openvals_score.toFixed(1)}</td>
                  <td className="p-3">
                    <a
                      className="text-foreground underline-offset-4 hover:underline"
                      href={item.source_url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      {item.source_type.replaceAll("_", " ")}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {trustCenter.items.length === 0 ? (
            <p className="p-5 text-sm text-muted-foreground">No autonomous evidence records yet.</p>
          ) : null}
        </div>
      </section>
    </div>
  );
}
