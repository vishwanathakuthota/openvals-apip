import { Badge } from "@/components/ui/badge";
import { fetchCompanyEvidenceTimeline } from "@/lib/api";

export default async function CompanyEvidenceTimelinePage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const timeline = await fetchCompanyEvidenceTimeline(id);
  const company = timeline.items[0]?.company ?? id;

  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">
          AI Economy Validation
        </p>
        <h1 className="text-4xl font-semibold">{company} Evidence Timeline</h1>
      </header>
      <div className="grid gap-3">
        {timeline.items.map((item) => (
          <article className="grid gap-3 rounded-lg border border-border bg-card p-5" key={item.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">{item.metric_name}</h2>
                <p className="text-sm text-muted-foreground">{item.evidence_text}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge>{item.evidence_classification}</Badge>
                <Badge>{item.status}</Badge>
              </div>
            </div>
            <div className="grid gap-3 text-sm text-muted-foreground md:grid-cols-4">
              <span>Collected: {formatDate(item.collection_timestamp)}</span>
              <span>Validated: {formatDate(item.validation_timestamp)}</span>
              <span>Approved: {formatDate(item.approved_at)}</span>
              <span>Published: {formatDate(item.published_at)}</span>
            </div>
          </article>
        ))}
        {timeline.items.length === 0 ? (
          <p className="rounded-lg border border-border p-5 text-sm text-muted-foreground">
            No evidence records are available yet.
          </p>
        ) : null}
      </div>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );
}
