import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Database, Gauge, ShieldCheck } from "lucide-react";

import { BetaSignupForm } from "@/components/beta-signup-form";
import { ConfidenceScore } from "@/components/confidence-score";
import { MetricCard } from "@/components/metric-card";
import { RealityIndexLeaderboard } from "@/components/reality-index-leaderboard";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchScoreboard } from "@/lib/api";

export const metadata: Metadata = {
  title: "Public Beta",
  description:
    "Join the APIP public beta from OpenVals, the source-backed trust platform for AI profitability intelligence.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "APIP Public Beta by OpenVals",
    description:
      "Source-backed AI profitability intelligence with confidence, evidence coverage, and Trust Index transparency.",
    url: "/",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP Public Beta" }]
  }
};

const proofPoints = [
  {
    title: "Source-backed metrics",
    body: "Published numbers are paired with source URLs, evidence coverage, freshness, and reviewer history.",
    icon: Database
  },
  {
    title: "Trust over hype",
    body: "OpenVals Trust Index measures evidence quality and methodology transparency, not company quality.",
    icon: ShieldCheck
  },
  {
    title: "Built for verification",
    body: "Users can trace where a metric came from, why it was published, and how confidence was calculated.",
    icon: Gauge
  }
];

const launchScope = [
  "Gold Standard validation workflows",
  "AI Reality Index and Trust Index leaderboards",
  "Public APIs with API key access",
  "Company evidence timelines and source lineage"
];

export default async function HomePage() {
  const scoreboard = await fetchScoreboard();
  const topRealityIndex = scoreboard.top_ai_reality_index[0];

  return (
    <>
      <section className="grid min-h-[calc(100vh-9rem)] gap-8 border-b border-border pb-8 xl:grid-cols-[1.05fr_0.95fr] xl:items-center">
        <div className="grid gap-6">
          <div className="grid gap-3">
            <Badge className="w-fit border-primary text-primary">Public beta preparing for launch</Badge>
            <h1 className="max-w-4xl text-4xl font-semibold tracking-normal md:text-6xl">
              The trust platform for AI profitability intelligence.
            </h1>
            <p className="max-w-3xl text-base leading-7 text-muted-foreground md:text-lg">
              APIP by OpenVals helps investors, researchers, operators, and policy teams answer whether AI investment is
              producing measurable economic value. Every public metric is designed to show source, confidence, coverage,
              last updated date, and methodology context.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              className="inline-flex h-11 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground"
              href="#beta-signup"
            >
              Join Beta
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <Link
              className="inline-flex h-11 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium"
              href="/trust-center"
            >
              View Trust Center
            </Link>
            <Link
              className="inline-flex h-11 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium"
              href="/developers"
            >
              Explore API
            </Link>
          </div>
          <div className="grid gap-3 rounded-lg border border-border bg-card p-4">
            <strong>Public beta disclaimer</strong>
            <p className="text-sm leading-6 text-muted-foreground">
              APIP data is source-backed. Some metrics are estimated or derived when companies do not directly disclose
              AI-specific economics. Trust Index measures evidence quality, source transparency, and reproducibility; it
              does not measure company quality or investment merit.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <div className="grid gap-4 md:grid-cols-2">
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
          </div>
          <ConfidenceScore confidence={scoreboard.confidence} />
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {proofPoints.map((point) => {
          const Icon = point.icon;
          return (
            <Card key={point.title}>
              <CardHeader>
                <Icon className="h-5 w-5 text-primary" aria-hidden />
                <CardTitle>{point.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-6 text-muted-foreground">{point.body}</p>
              </CardContent>
            </Card>
          );
        })}
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Beta Launch Scope</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {launchScope.map((item) => (
              <div className="flex items-start gap-2" key={item}>
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-primary" aria-hidden />
                <span className="text-sm text-muted-foreground">{item}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <RealityIndexLeaderboard items={scoreboard.top_ai_reality_index} />
      </section>

      <section className="grid gap-4 rounded-lg border border-border bg-card p-5 xl:grid-cols-[0.85fr_1.15fr]" id="beta-signup">
        <div className="grid content-start gap-2">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Beta access</p>
          <h2 className="text-2xl font-semibold">Join the APIP public beta waitlist</h2>
          <p className="text-sm leading-6 text-muted-foreground">
            Tell us what you want to validate. OpenVals will prioritize researchers, investors, operators, and enterprise
            teams that need source-backed AI economics.
          </p>
        </div>
        <BetaSignupForm compact />
      </section>
    </>
  );
}
