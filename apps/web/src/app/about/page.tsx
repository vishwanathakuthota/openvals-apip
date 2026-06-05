import type { Metadata } from "next";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "About",
  description: "About OpenVals APIP, the AI Profitability Intelligence Platform."
};

export default function AboutPage() {
  return (
    <>
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">About OpenVals APIP</p>
        <h1 className="max-w-3xl text-4xl font-semibold">Evidence infrastructure for the AI economy</h1>
        <p className="max-w-3xl leading-7 text-muted-foreground">
          OpenVals APIP is built to make AI economics inspectable: what companies spend, what they earn, how confidence
          is calculated, and where each claim comes from.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["Mission", "Answer whether AI is profitable yet with auditable metrics and transparent scoring."],
          ["Scope", "Track company, industry, country, and model-level economics for Version 1 launch."],
          ["Principle", "Show evidence quality beside every number so users can judge the claim, not just the chart."]
        ].map(([title, copy]) => (
          <Card key={title}>
            <CardHeader>
              <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{copy}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
