"use client";

import { Info, X } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { entityName } from "@/lib/fallback-data";
import { cn } from "@/lib/utils";
import type { RealityIndexItem } from "@/types/api";

export function RealityIndexLeaderboard({ items }: { items: RealityIndexItem[] }) {
  const [open, setOpen] = useState(false);
  const topScore = items[0]?.score ?? 0;
  const topConfidence = items[0]?.confidence;

  return (
    <>
      <Card>
        <CardHeader className="flex-row items-start justify-between gap-3">
          <div className="grid gap-1">
            <CardTitle>AI Reality Index</CardTitle>
            <span className="text-sm text-muted-foreground">
              Top score {topScore.toFixed(1)}
              {topConfidence ? ` - ${topConfidence.source_count} sources` : ""}
            </span>
          </div>
          <Button aria-label="Explain AI Reality Index" onClick={() => setOpen(true)} size="icon" variant="outline">
            <Info className="h-4 w-4" aria-hidden />
          </Button>
        </CardHeader>
        <CardContent className="grid gap-3">
          {items.map((item, index) => (
            <article
              className="grid gap-3 border-b border-border pb-3 last:border-0 last:pb-0 md:grid-cols-[48px_1fr_92px_132px_160px]"
              key={`${item.entity_type}-${item.entity_id}`}
            >
              <span className="text-muted-foreground">#{index + 1}</span>
              <div className="grid gap-1">
                <strong>{item.entity_name ?? entityName(item.entity_id)}</strong>
                <span className="text-xs uppercase text-muted-foreground">{item.entity_type}</span>
              </div>
              <span className="font-semibold tabular-nums">{item.score.toFixed(1)}</span>
              <Badge className={classificationClass(item.classification ?? item.label)}>
                {item.classification ?? item.label}
              </Badge>
              <div className="text-xs text-muted-foreground">
                <span className="block">{item.source_count ?? item.confidence?.source_count ?? 0} sources</span>
                <span className="block">{formatDate(item.last_updated ?? item.confidence?.last_updated)}</span>
              </div>
            </article>
          ))}
        </CardContent>
      </Card>
      {open ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-background/80 p-4 backdrop-blur-sm">
          <section className="w-full max-w-xl rounded-lg border border-border bg-card shadow-2xl">
            <header className="flex items-center justify-between gap-3 border-b border-border p-5">
              <h2 className="text-lg font-semibold">AI Reality Index Formula</h2>
              <Button aria-label="Close explanation" onClick={() => setOpen(false)} size="icon" variant="ghost">
                <X className="h-4 w-4" aria-hidden />
              </Button>
            </header>
            <div className="grid gap-4 p-5 text-sm text-muted-foreground">
              <p className="text-foreground">
                AI Reality Index = ROI x 0.4 + Revenue Growth x 0.3 + Margin x 0.2 + Adoption x 0.1
              </p>
              <div className="grid gap-2">
                {[
                  ["90-100", "Elite"],
                  ["70-89", "Strong"],
                  ["50-69", "Emerging"],
                  ["30-49", "Speculative"],
                  ["0-29", "Cash Burn Zone"]
                ].map(([range, label]) => (
                  <div className="flex items-center justify-between border-b border-border/70 py-2" key={label}>
                    <span>{range}</span>
                    <Badge className={classificationClass(label)}>{label}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}

function classificationClass(label: string) {
  return cn(
    label === "Elite" && "border-emerald-400 text-emerald-300",
    label === "Strong" && "border-primary/60 text-primary",
    label === "Emerging" && "border-sky-400 text-sky-300",
    label === "Speculative" && "border-amber-400 text-amber-300",
    label === "Cash Burn Zone" && "border-red-400 text-red-300"
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
