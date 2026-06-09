import { Badge } from "@/components/ui/badge";
import { fetchCompanySourceLineage } from "@/lib/api";

export default async function CompanySourceLineagePage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const lineage = await fetchCompanySourceLineage(id);

  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">
          AI Economy Validation
        </p>
        <h1 className="text-4xl font-semibold">{lineage.company} Source Lineage</h1>
      </header>
      <section className="grid gap-3">
        {lineage.items.map((item) => (
          <article className="grid gap-3 rounded-lg border border-border bg-card p-5" key={item.source_url}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <a
                className="font-medium text-foreground underline-offset-4 hover:underline"
                href={item.source_url}
                rel="noreferrer"
                target="_blank"
              >
                {item.source_url}
              </a>
              <Badge>{item.evidence_classification}</Badge>
            </div>
            <div className="grid gap-2 text-sm text-muted-foreground md:grid-cols-4">
              <span>Type: {item.source_type.replaceAll("_", " ")}</span>
              <span>Confidence: {item.confidence.toFixed(1)}</span>
              <span>Coverage: {item.evidence_coverage.toFixed(1)}%</span>
              <span>Reviewer: {item.reviewer ?? "n/a"}</span>
            </div>
          </article>
        ))}
        {lineage.items.length === 0 ? (
          <p className="rounded-lg border border-border p-5 text-sm text-muted-foreground">
            No public lineage records are available yet.
          </p>
        ) : null}
      </section>
    </div>
  );
}
