import { MetricTable } from "@/components/metric-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchAiEconomicsReport, fetchEntity } from "@/lib/api";
import { formatMetric } from "@/lib/format";

export default async function CompanyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [company, economics] = await Promise.all([
    fetchEntity("companies", id),
    fetchAiEconomicsReport(id)
  ]);
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Company Dashboard</p>
        <h1 className="text-4xl font-semibold">{company.name}</h1>
        <p className="text-muted-foreground">{company.ticker ?? company.slug}</p>
      </header>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <EconomicsCard
          confidence={economics.confidence_score}
          label="AI Revenue Estimate"
          lastUpdated={economics.last_updated}
          sourceCount={economics.source_count}
          unit="usd"
          value={economics.ai_revenue_estimate}
        />
        <EconomicsCard
          confidence={economics.confidence_score}
          label="AI Investment"
          lastUpdated={economics.last_updated}
          sourceCount={economics.source_count}
          unit="usd"
          value={economics.ai_investment}
        />
        <EconomicsCard
          confidence={economics.confidence_score}
          label="Infrastructure Spend"
          lastUpdated={economics.last_updated}
          sourceCount={economics.source_count}
          unit="usd"
          value={economics.infrastructure_spend}
        />
        <EconomicsCard
          confidence={economics.confidence_score}
          label="AI Profitability Score"
          lastUpdated={economics.last_updated}
          sourceCount={economics.source_count}
          unit="score"
          value={economics.ai_profitability_score}
        />
      </section>
      <MetricTable metrics={company.metrics ?? []} />
    </>
  );
}

function EconomicsCard({
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
      <CardHeader>
        <CardTitle className="text-sm text-muted-foreground">{label}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3">
        <strong className="text-2xl">{formatMetric(value, unit)}</strong>
        <div className="grid gap-1 text-xs text-muted-foreground">
          <span>Confidence {confidence.toFixed(1)}</span>
          <span>{sourceCount} sources</span>
          <span>{formatDate(lastUpdated)}</span>
        </div>
      </CardContent>
    </Card>
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
