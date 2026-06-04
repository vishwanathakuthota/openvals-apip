export default function AdminPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Operations</p>
        <h1 className="text-4xl font-semibold">Admin Portal</h1>
      </header>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {["Source Approval", "Metric Editing", "ETL Execution", "CSV Import"].map((label) => (
          <article className="rounded-lg border border-border bg-card p-5" key={label}>
            <span>{label}</span>
            <strong className="mt-3 block">Ready for backend workflow expansion</strong>
          </article>
        ))}
      </div>
    </>
  );
}
