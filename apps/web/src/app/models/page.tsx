import { EntityDirectory } from "@/components/entity-directory";
import { fetchCollection } from "@/lib/api";

export default async function ModelsPage() {
  const data = await fetchCollection("models");
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Model Economics</p>
        <h1 className="text-4xl font-semibold">Models</h1>
      </header>
      <EntityDirectory basePath="/models" items={data.items} />
    </>
  );
}
