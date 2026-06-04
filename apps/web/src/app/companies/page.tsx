import { EntityDirectory } from "@/components/entity-directory";
import { fetchCollection } from "@/lib/api";

export default async function CompaniesPage() {
  const data = await fetchCollection("companies");
  return (
    <>
      <PageHeader eyebrow="Company Dashboard" title="Companies" />
      <EntityDirectory basePath="/companies" items={data.items} />
    </>
  );
}

function PageHeader({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <header className="grid gap-2 border-b border-border pb-6">
      <p className="text-xs font-semibold uppercase text-muted-foreground">{eyebrow}</p>
      <h1 className="text-4xl font-semibold">{title}</h1>
    </header>
  );
}
