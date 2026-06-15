import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchAiEconomics } from "@/lib/api";
import { formatMetric } from "@/lib/format";

export default async function AiEconomicsPage() {
  const economics = await fetchAiEconomics();
  const top = economics.ai_profitability[0];

  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">AI Economics Intelligence Engine</p>
        <h1 className="text-4xl font-semibold">AI Economics Dashboard</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          APIP estimates AI revenue, AI investment, infrastructure spend, and profitability from approved evidence
          records. Every widget exposes source count, confidence, and freshness metadata.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <EconomicsSummaryCard
          label="Estimated AI Revenue"
          value={economics.summary.estimated_ai_revenue}
          unit="usd"
          confidence={economics.summary.average_confidence_score}
          sourceCount={economics.summary.source_count}
          lastUpdated={economics.summary.last_updated}
        />
        <EconomicsSummaryCard
          label="Estimated AI Investment"
          value={economics.summary.estimated_ai_investment}
          unit="usd"
          confidence={economics.summary.average_confidence_score}
          sourceCount={economics.summary.source_count}
          lastUpdated={economics.summary.last_updated}
        />
        <EconomicsSummaryCard
          label="Estimated AI Profit"
          value={economics.summary.estimated_ai_profit}
          unit="usd"
          confidence={economics.summary.average_confidence_score}
          sourceCount={economics.summary.source_count}
          lastUpdated={economics.summary.last_updated}
        />
        <EconomicsSummaryCard
          label="Average Profitability"
          value={economics.summary.average_profitability_score}
          unit="score"
          confidence={economics.summary.average_confidence_score}
          sourceCount={economics.summary.source_count}
          lastUpdated={economics.summary.last_updated}
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader className="flex-row items-start justify-between gap-4">
            <div>
              <CardTitle>AI Profitability Leader</CardTitle>
              <p className="text-sm text-muted-foreground">Highest current AI Profitability Score.</p>
            </div>
            <Badge>{top?.classification ?? "n/a"}</Badge>
          </CardHeader>
          <CardContent className="grid gap-4">
            {top ? (
              <>
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">{top.company}</p>
                    <strong className="text-5xl">{top.score.toFixed(1)}</strong>
                  </div>
                  <Link className="text-sm text-primary" href="/ai-profitability">
                    View leaderboard
                  </Link>
                </div>
                <MetadataRow
                  confidence={top.confidence_score}
                  sourceCount={top.source_count}
                  lastUpdated={top.last_updated}
                />
                <p className="rounded-md border border-border bg-muted/40 p-3 text-sm text-muted-foreground">
                  {top.methodology_note}
                </p>
              </>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Methodology</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm text-muted-foreground">
            <p>{economics.summary.methodology_note}</p>
            <div className="grid gap-2 rounded-md border border-border bg-muted/30 p-3">
              <span>Revenue inputs: revenue, earnings calls, investor presentations, SEC filings, disclosures.</span>
              <span>Investment outputs: AI investment, AI R&amp;D spend, infrastructure spend.</span>
              <span>
                Profitability formula: 25% Revenue Efficiency, 20% AI Revenue Growth, 20% AI Margin Proxy, 20%
                Infrastructure ROI, 15% Capital Efficiency.
              </span>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>AI Revenue Estimates</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {economics.ai_revenue.slice(0, 10).map((item) => (
              <div className="grid gap-2 rounded-md border border-border p-3" key={item.company_slug}>
                <div className="flex items-center justify-between gap-3">
                  <strong>{item.company}</strong>
                  <span>{formatMetric(item.ai_revenue_estimate, "usd")}</span>
                </div>
                <MetadataRow
                  confidence={item.confidence_score}
                  sourceCount={item.source_count}
                  lastUpdated={item.last_updated}
                />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Investment Estimates</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {economics.ai_investment.slice(0, 10).map((item) => (
              <div className="grid gap-2 rounded-md border border-border p-3" key={item.company_slug}>
                <div className="flex items-center justify-between gap-3">
                  <strong>{item.company}</strong>
                  <span>{formatMetric(item.ai_investment, "usd")}</span>
                </div>
                <div className="grid gap-1 text-xs text-muted-foreground sm:grid-cols-2">
                  <span>AI R&amp;D: {formatMetric(item.ai_rd_spend, "usd")}</span>
                  <span>Infrastructure: {formatMetric(item.infrastructure_spend, "usd")}</span>
                </div>
                <MetadataRow
                  confidence={item.confidence_score}
                  sourceCount={item.source_count}
                  lastUpdated={item.last_updated}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </>
  );
}

function EconomicsSummaryCard({
  label,
  value,
  unit,
  confidence,
  sourceCount,
  lastUpdated
}: {
  label: string;
  value: number;
  unit: string;
  confidence: number;
  sourceCount: number;
  lastUpdated: string;
}) {
  return (
    <Card>
      <CardContent className="grid gap-3 p-5">
        <span className="text-sm text-muted-foreground">{label}</span>
        <strong className="text-2xl">{formatMetric(value, unit)}</strong>
        <MetadataRow confidence={confidence} sourceCount={sourceCount} lastUpdated={lastUpdated} />
      </CardContent>
    </Card>
  );
}

function MetadataRow({
  confidence,
  sourceCount,
  lastUpdated
}: {
  confidence: number;
  sourceCount: number;
  lastUpdated: string;
}) {
  return (
    <div className="grid gap-1 text-xs text-muted-foreground sm:grid-cols-3">
      <span>Confidence {confidence.toFixed(1)}</span>
      <span>{sourceCount} sources</span>
      <span>{formatDate(lastUpdated)}</span>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(
    new Date(value)
  );
}
