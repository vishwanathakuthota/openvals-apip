import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchTrustLeaderboard } from "@/lib/api";

export const metadata: Metadata = {
  title: "Trust Leaderboard | APIP",
  description: "Company leaderboard ranked by OpenVals Trust Index."
};

export default async function LeaderboardPage() {
  const leaderboard = await fetchTrustLeaderboard();
  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Leaderboard</p>
        <h1 className="text-4xl font-semibold">OpenVals Trust Leaderboard</h1>
        <p className="max-w-3xl text-muted-foreground">
          Companies ranked by confidence, evidence coverage, transparency, reproducibility, and source quality.
        </p>
      </header>
      <Card>
        <CardHeader>
          <CardTitle>Company Trust Ranking</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-border text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-3 pr-3">Rank</th>
                <th className="py-3 pr-3">Company</th>
                <th className="py-3 pr-3">Trust Index</th>
                <th className="py-3 pr-3">Rating</th>
                <th className="py-3 pr-3">Sources</th>
                <th className="py-3 pr-3">Published Records</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.items.map((item, index) => (
                <tr className="border-b border-border/70" key={item.entity_id ?? item.entity_name}>
                  <td className="py-3 pr-3 tabular-nums">{index + 1}</td>
                  <td className="py-3 pr-3 font-medium">{item.entity_name}</td>
                  <td className="py-3 pr-3 tabular-nums">{item.trust_index.toFixed(1)}</td>
                  <td className="py-3 pr-3">
                    <Badge>{item.trust_rating}</Badge>
                  </td>
                  <td className="py-3 pr-3 tabular-nums">{item.source_count}</td>
                  <td className="py-3 pr-3 tabular-nums">{item.published_record_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
