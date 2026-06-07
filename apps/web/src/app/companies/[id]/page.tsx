import { MetricTable } from "@/components/metric-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchEntity } from "@/lib/api";

export default async function CompanyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const company = await fetchEntity("companies", id);
  const trustIndex = company.trust_index;

  return (
    <div className="grid gap-6">
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Company Dashboard</p>
        <h1 className="text-4xl font-semibold">{company.name}</h1>
        <p className="text-muted-foreground">{company.ticker ?? company.slug}</p>
      </header>
      {trustIndex ? (
        <section className="grid gap-4 lg:grid-cols-[1fr_2fr]">
          <Card>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">
                OpenVals Trust Index
              </p>
              <CardTitle className="text-4xl tabular-nums">
                {trustIndex.trust_index.toFixed(1)}
              </CardTitle>
              <div className="flex flex-wrap gap-2">
                <Badge>{trustIndex.trust_rating}</Badge>
                <Badge>{trustIndex.trust_classification}</Badge>
              </div>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              {trustIndex.published_record_count} published records across{" "}
              {trustIndex.source_count} source{trustIndex.source_count === 1 ? "" : "s"}.
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Trust Components</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3">
              {Object.entries(trustIndex.components).map(([label, value]) => (
                <div className="grid gap-1" key={label}>
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="capitalize text-muted-foreground">
                      {label.replaceAll("_", " ")}
                    </span>
                    <span className="tabular-nums">{value.toFixed(1)}</span>
                  </div>
                  <Progress value={value} />
                </div>
              ))}
            </CardContent>
          </Card>
        </section>
      ) : null}
      <MetricTable metrics={company.metrics ?? []} />
    </div>
  );
}
