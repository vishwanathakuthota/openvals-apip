import { notFound } from "next/navigation";

import { MetricTable } from "@/components/metric-table";
import { fetchEntity } from "@/lib/api";

export default async function CompanyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const company = await fetchEntity("companies", id);
  if (!company) {
    notFound();
  }
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Company Dashboard</p>
        <h1 className="text-4xl font-semibold">{company.name}</h1>
        <p className="text-muted-foreground">{company.ticker ?? company.slug}</p>
      </header>
      <MetricTable metrics={company.metrics ?? []} />
    </>
  );
}
