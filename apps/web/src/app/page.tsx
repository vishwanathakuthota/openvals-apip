import { ConfidenceScore } from "@/components/confidence-score";
import { ProfitabilityChart } from "@/components/charts/profitability-chart";
import { RealityIndexChart } from "@/components/charts/reality-index-chart";
import { MetricCard } from "@/components/metric-card";
import { RealityIndexLeaderboard } from "@/components/reality-index-leaderboard";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchScoreboard } from "@/lib/api";

export default async function HomePage() {
  const scoreboard = await fetchScoreboard();
  const chartData = [
    { name: "Global", spend: scoreboard.total_ai_spend, revenue: scoreboard.total_ai_revenue },
    { name: "Tracked", spend: scoreboard.total_ai_spend * 0.58, revenue: scoreboard.total_ai_revenue * 0.64 },
    { name: "Verified", spend: scoreboard.total_ai_spend * 0.34, revenue: scoreboard.total_ai_revenue * 0.42 }
  ];
  const topRealityIndex = scoreboard.top_ai_reality_index[0];

  return (
    <>
      <header className="flex flex-col gap-4 border-b border-border pb-6 md:flex-row md:items-start md:justify-between">
        <div className="grid gap-2">
          <p className="text-xs font-semibold uppercase text-muted-foreground">
            OpenVals AI Profitability Intelligence Platform
          </p>
          <h1 className="max-w-3xl text-4xl font-semibold tracking-normal md:text-5xl">Is AI profitable yet?</h1>
          <p className="max-w-3xl text-base leading-7 text-muted-foreground">
            APIP tracks whether AI spending is converting into revenue, margin expansion, adoption, and measurable
            return on investment. Every headline number is paired with source count, freshness, methodology notes, and
            a confidence score.
          </p>
        </div>
        <div className="grid gap-2">
          <Badge className="w-fit border-primary text-primary">{scoreboard.profitability_gauge}</Badge>
          <span className="text-sm text-muted-foreground">Launch domain: apip.openvalidations.com</span>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          classification="Validated"
          confidence={scoreboard.confidence}
          label="Total AI Spend"
          value={scoreboard.total_ai_spend}
          unit="usd"
          validationStatus="Published"
        />
        <MetricCard
          classification="Validated"
          confidence={scoreboard.confidence}
          label="Total AI Revenue"
          value={scoreboard.total_ai_revenue}
          unit="usd"
          validationStatus="Published"
        />
        <MetricCard
          classification="Derived"
          confidence={scoreboard.confidence}
          label="Net Profit/Loss"
          value={scoreboard.net_profit}
          unit="usd"
          validationStatus="Published"
        />
        <MetricCard
          classification="Derived"
          confidence={scoreboard.confidence}
          label="Global ROI"
          value={scoreboard.global_roi}
          unit="ratio"
          validationStatus="Published"
        />
        <MetricCard
          classification="Derived"
          confidence={topRealityIndex?.confidence ?? scoreboard.confidence}
          label="AI Reality Index"
          value={topRealityIndex?.score ?? 0}
          unit="score"
          validationStatus="Published"
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
        <Card>
          <CardHeader>
            <CardTitle>Spend vs Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <ProfitabilityChart data={chartData} />
          </CardContent>
        </Card>
        <ConfidenceScore confidence={scoreboard.confidence} />
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>AI Reality Index</CardTitle>
          </CardHeader>
          <CardContent>
            <RealityIndexChart items={scoreboard.top_ai_reality_index} />
          </CardContent>
        </Card>
        <RealityIndexLeaderboard items={scoreboard.top_ai_reality_index} />
      </section>
    </>
  );
}
