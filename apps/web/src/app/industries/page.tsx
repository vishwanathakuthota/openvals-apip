import { EntityDirectory } from "@/components/entity-directory";
import { fetchCollection } from "@/lib/api";

export default async function IndustriesPage() {
  const data = await fetchCollection("industries");
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Profitability Heatmaps</p>
        <h1 className="text-4xl font-semibold">Industries</h1>
      </header>
      <EntityDirectory basePath="/industries" items={data.items} />
    </>
  );
}
