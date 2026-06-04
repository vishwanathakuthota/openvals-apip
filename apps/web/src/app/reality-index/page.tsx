import { RealityIndexChart } from "@/components/charts/reality-index-chart";
import { RealityIndexLeaderboard } from "@/components/reality-index-leaderboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchRealityIndex } from "@/lib/api";

export default async function RealityIndexPage() {
  const realityIndex = await fetchRealityIndex();
  const items = realityIndex.items;
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
            <RealityIndexChart items={items} />
          </CardContent>
        </Card>
        <RealityIndexLeaderboard items={items} />
      </section>
    </>
  );
}
