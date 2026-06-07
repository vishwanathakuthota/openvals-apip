import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { fetchAlphabetEvidenceTimeline } from "@/lib/api";

export const metadata: Metadata = {
  title: "Alphabet Evidence Timeline | APIP",
  description: "End-to-end Alphabet evidence timeline from collection through publication."
};

export default async function AlphabetEvidenceTimelinePage() {
  const timeline = await fetchAlphabetEvidenceTimeline();
  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Alphabet Gold Standard</p>
        <h1 className="text-4xl font-semibold">Evidence Timeline</h1>
      </header>
      <div className="grid gap-3">
        {timeline.items.map((item) => (
          <article className="grid gap-3 rounded-lg border border-border bg-card p-5" key={item.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">{item.metric_name}</h2>
                <p className="text-sm text-muted-foreground">{item.evidence_text}</p>
              </div>
              <Badge>{item.status}</Badge>
            </div>
            <div className="grid gap-3 text-sm text-muted-foreground md:grid-cols-4">
              <span>Collected: {formatDate(item.collection_timestamp)}</span>
              <span>Validated: {formatDate(item.validation_timestamp)}</span>
              <span>Approved: {formatDate(item.approved_at)}</span>
              <span>Published: {formatDate(item.published_at)}</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}
