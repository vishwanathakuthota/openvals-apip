import { notFound } from "next/navigation";

import { MetricTable } from "@/components/metric-table";
import { fetchEntity } from "@/lib/api";

export default async function ModelPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const model = await fetchEntity("models", id);
  if (!model) {
    notFound();
  }
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Model Economics</p>
        <h1 className="text-4xl font-semibold">{model.name}</h1>
        <p className="text-muted-foreground">{model.model_family}</p>
      </header>
      <MetricTable metrics={model.metrics ?? []} />
    </>
  );
}
