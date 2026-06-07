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
            <CardTitle>OpenVals Trust Index</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="flex items-end justify-between gap-3">
              <div>
                <p className="text-4xl font-semibold tabular-nums">
                  {trustCenter.trust_index?.trust_index.toFixed(1) ?? "0.0"}
                </p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge>{trustCenter.trust_index?.trust_rating ?? "Low Trust"}</Badge>
                  <Badge>
                    {trustCenter.trust_index?.trust_classification ?? "Insufficient Evidence"}
                  </Badge>
                </div>
              </div>
              <p className="text-right text-sm text-muted-foreground">
                {trustCenter.trust_index?.published_record_count ?? 0} published records
              </p>
            </div>
            <Progress value={trustCenter.trust_index?.trust_index ?? 0} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Trust Trend</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {(trustCenter.trust_trend ?? []).slice(0, 5).map((snapshot) => (
              <div className="grid gap-1" key={`${snapshot.entity_name}-${snapshot.snapshot_date}`}>
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span>{snapshot.entity_name}</span>
                  <span className="tabular-nums">{snapshot.trust_index.toFixed(1)}</span>
                </div>
                <Progress value={snapshot.trust_index} />
              </div>
            ))}
            {(trustCenter.trust_trend ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No Trust Index snapshots yet.</p>
            ) : null}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Trust Change Notifications</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {(trustCenter.trust_notifications ?? []).slice(0, 6).map((item) => (
              <div className="grid gap-1 rounded-md border border-border p-3" key={item.id}>
                <div className="flex items-center justify-between gap-3">
                  <strong className="text-sm">{item.entity_name}</strong>
                  <Badge>{item.change_amount >= 0 ? "+" : ""}{item.change_amount.toFixed(1)}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{item.message}</p>
              </div>
            ))}
            {(trustCenter.trust_notifications ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No Trust Index notifications yet.</p>
            ) : null}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Trust Methodology</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm text-muted-foreground">
            <p>{trustCenter.methodology?.formula}</p>
            {trustCenter.trust_index ? (
              <div className="grid gap-2">
                {Object.entries(trustCenter.trust_index.weights).map(([label, value]) => (
                  <div className="flex items-center justify-between gap-3" key={label}>
                    <span className="capitalize">{label.replaceAll("_", " ")}</span>
                    <span className="tabular-nums">{(value * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            ) : null}
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
