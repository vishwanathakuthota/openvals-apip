import { EntityDirectory } from "@/components/entity-directory";
import { fetchCollection } from "@/lib/api";

export default async function CountriesPage() {
  const data = await fetchCollection("countries");
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Country Dashboard</p>
        <h1 className="text-4xl font-semibold">Countries</h1>
      </header>
      <EntityDirectory basePath="/countries" items={data.items} />
    </>
  );
}
