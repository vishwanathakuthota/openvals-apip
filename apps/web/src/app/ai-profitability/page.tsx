import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchAiProfitability } from "@/lib/api";

const componentLabels = {
  revenue_efficiency: "Revenue Efficiency",
  ai_revenue_growth: "AI Revenue Growth",
  ai_margin_proxy: "AI Margin Proxy",
  infrastructure_roi: "Infrastructure ROI",
  capital_efficiency: "Capital Efficiency"
};

export default async function AiProfitabilityPage() {
  const profitability = await fetchAiProfitability();

  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">AI Profitability Score</p>
        <h1 className="text-4xl font-semibold">AI Profitability Leaderboard</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Company rankings across revenue efficiency, AI revenue growth, margin proxy, infrastructure ROI, and capital
          efficiency.
        </p>
      </header>

      <section className="grid gap-4">
        {profitability.items.map((item, index) => (
          <Card key={item.company_slug}>
            <CardHeader className="gap-3 md:flex-row md:items-start md:justify-between">
              <div className="grid gap-1">
                <CardTitle className="flex flex-wrap items-center gap-3">
                  <span>#{index + 1}</span>
                  <span>{item.company}</span>
                  <Badge>{item.rating}</Badge>
                </CardTitle>
                <p className="text-sm text-muted-foreground">{item.classification}</p>
              </div>
              <div className="text-left md:text-right">
                <strong className="text-3xl">{item.score.toFixed(1)}</strong>
                <p className="text-xs text-muted-foreground">AI Profitability Score</p>
              </div>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="grid gap-2 md:grid-cols-5">
                {Object.entries(item.components).map(([key, value]) => (
                  <div className="grid gap-2 rounded-md border border-border p-3" key={key}>
                    <span className="min-h-8 text-xs text-muted-foreground">
                      {componentLabels[key as keyof typeof componentLabels]}
                    </span>
                    <strong>{value.toFixed(1)}</strong>
                    <Progress value={value} className="h-1.5" />
                  </div>
                ))}
              </div>
              <div className="grid gap-2 rounded-md border border-border bg-muted/30 p-3 text-xs text-muted-foreground md:grid-cols-4">
                <span>Confidence {item.confidence_score.toFixed(1)}</span>
                <span>{item.confidence_label}</span>
                <span>{item.source_count} sources</span>
                <span>{formatDate(item.last_updated)}</span>
              </div>
              <p className="text-sm text-muted-foreground">{item.formula}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
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
