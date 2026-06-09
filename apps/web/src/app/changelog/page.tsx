import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Changelog",
  description: "APIP public beta launch changelog and platform release notes.",
  alternates: { canonical: "/changelog" },
  openGraph: {
    title: "APIP Changelog",
    description: "Release notes for the OpenVals APIP public beta.",
    url: "/changelog",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP Changelog" }]
  }
};

const entries = [
  {
    version: "Public Beta Prep",
    date: "June 2026",
    items: [
      "Added public beta landing page and waitlist flow.",
      "Added OpenVals commercialization foundation, API plans, and developer portal updates.",
      "Expanded validation coverage for the AI economy company set.",
      "Added Trust Index, Trust Center, and source lineage visibility."
    ]
  },
  {
    version: "Trust Platform Foundation",
    date: "June 2026",
    items: [
      "Introduced Gold Standard validation workflows.",
      "Added Confidence Score, Evidence Coverage, and OpenVals Score engines.",
      "Added autonomous research queues with human approval before publishing."
    ]
  }
];

export default function ChangelogPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Release Notes</p>
        <h1 className="text-4xl font-semibold">APIP Changelog</h1>
      </header>
      <section className="grid gap-4">
        {entries.map((entry) => (
          <Card key={entry.version}>
            <CardHeader>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <CardTitle>{entry.version}</CardTitle>
                <Badge>{entry.date}</Badge>
              </div>
            </CardHeader>
            <CardContent className="grid gap-2">
              {entry.items.map((item) => (
                <p className="text-sm text-muted-foreground" key={item}>
                  {item}
                </p>
              ))}
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
