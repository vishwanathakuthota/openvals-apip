import { MetricTable } from "@/components/metric-table";
import { fetchEntity } from "@/lib/api";

export default async function CountryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const country = await fetchEntity("countries", id);
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Country Dashboard</p>
        <h1 className="text-4xl font-semibold">{country.name}</h1>
        <p className="text-muted-foreground">{country.region}</p>
      </header>
      <MetricTable metrics={country.metrics ?? []} />
    </>
  );
}
