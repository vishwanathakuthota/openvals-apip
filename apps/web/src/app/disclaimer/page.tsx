import type { Metadata } from "next";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Disclaimer",
  description: "Important limitations and usage terms for OpenVals APIP Version 1.",
  alternates: { canonical: "/disclaimer" },
  openGraph: {
    title: "APIP Disclaimer",
    description: "Public beta disclaimer for OpenVals APIP source-backed AI profitability intelligence.",
    url: "/disclaimer",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP Disclaimer" }]
  }
};

export default function DisclaimerPage() {
  return (
    <>
      <header className="grid gap-3 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Disclaimer</p>
        <h1 className="max-w-3xl text-4xl font-semibold">APIP is intelligence, not investment advice</h1>
        <p className="max-w-3xl leading-7 text-muted-foreground">
          Version 1 is designed for research, benchmarking, and source inspection. It should not be used as the sole
          basis for investment, legal, accounting, procurement, or strategic decisions.
        </p>
      </header>

      <section className="grid gap-4 lg:grid-cols-2">
        {[
          [
            "Data limitations",
            "APIP data is source-backed, but metrics can be incomplete, delayed, revised, or dependent on source methodology."
          ],
          [
            "Estimated metrics",
            "Some metrics are estimated or derived when companies do not directly disclose AI-specific economics."
          ],
          [
            "Trust Index scope",
            "Trust Index measures evidence quality, source transparency, and reproducibility. It does not measure company quality, investment quality, or management quality."
          ],
          [
            "Forward-looking claims",
            "Analyst estimates, industry forecasts, and management commentary can change quickly and may not reflect realized economics."
          ],
          [
            "No fiduciary relationship",
            "OpenVals APIP does not provide personalized investment, tax, legal, accounting, or financial advice."
          ],
          [
            "User responsibility",
            "Users should verify material claims against original sources and apply their own professional judgment before acting."
          ]
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
