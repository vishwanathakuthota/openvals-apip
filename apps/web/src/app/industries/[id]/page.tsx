import { notFound } from "next/navigation";

import { MetricTable } from "@/components/metric-table";
import { fetchEntity } from "@/lib/api";

export default async function IndustryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const industry = await fetchEntity("industries", id);
  if (!industry) {
    notFound();
  }
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Industry Dashboard</p>
        <h1 className="text-4xl font-semibold">{industry.name}</h1>
      </header>
      <MetricTable metrics={industry.metrics ?? []} />
    </>
  );
}
