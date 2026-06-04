import { RealityIndexChart } from "@/components/charts/reality-index-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchScoreboard } from "@/lib/api";
import { entityName } from "@/lib/fallback-data";

export default async function RealityIndexPage() {
  const scoreboard = await fetchScoreboard();
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Proprietary Score</p>
        <h1 className="text-4xl font-semibold">AI Reality Index</h1>
      </header>
      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Index Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <RealityIndexChart items={scoreboard.top_ai_reality_index} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Rankings</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {scoreboard.top_ai_reality_index.map((item, index) => (
              <div className="grid grid-cols-[48px_1fr_90px_120px] gap-3 border-b border-border pb-3" key={item.entity_id}>
                <span className="text-muted-foreground">#{index + 1}</span>
                <strong>{entityName(item.entity_id)}</strong>
                <span>{item.score}</span>
                <Badge>{item.label}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </>
  );
}
