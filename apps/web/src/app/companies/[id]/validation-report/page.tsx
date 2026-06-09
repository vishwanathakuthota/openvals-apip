import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchCompanyValidationReport } from "@/lib/api";

export default async function CompanyValidationReportPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const report = await fetchCompanyValidationReport(id);
  const summary = [
    ["OpenVals Validation", `${report.openvals_validation_score.toFixed(1)}%`],
    ["Evidence Coverage", `${report.evidence_coverage_score.toFixed(1)}%`],
    ["Sections", String(report.sections.length)],
    ["Lineage Records", String(report.source_lineage.length)]
  ];

  return (
    <div className="grid gap-8">
      <header className="grid gap-4 border-b border-border pb-6">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-xs font-semibold uppercase text-muted-foreground">
            AI Economy Validation
          </p>
          <Badge>{report.methodology_version}</Badge>
          <Badge>{report.status.replaceAll("_", " ")}</Badge>
          {report.validation_label ? <Badge>{report.validation_label}</Badge> : null}
        </div>
        <div className="grid gap-2">
          <h1 className="text-4xl font-semibold">{report.company} Validation Report</h1>
          <p className="max-w-3xl text-muted-foreground">{report.methodology_trace}</p>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        {summary.map(([label, value]) => (
          <Card key={label}>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p>
              <CardTitle className="text-2xl">{value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Validation Artifacts</p>
        <div className="flex flex-wrap gap-2">
          {[
            [`/companies/${id}/evidence-timeline`, "Evidence Timeline"],
            [`/companies/${id}/source-lineage`, "Source Lineage"],
            [`/companies/${id}/openvals-score`, "OpenVals Score"],
            [`/companies/${id}/trust-report`, "Trust Report"]
          ].map(([href, label]) => (
            <Link
              className="rounded-md border border-border px-3 py-2 text-sm text-muted-foreground hover:text-foreground"
              href={href}
              key={href}
            >
              {label}
            </Link>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle>Validation Score</CardTitle>
            <p className="text-sm text-muted-foreground">{report.openvals_validation_label}</p>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Progress value={report.openvals_validation_score} />
            <p className="text-sm text-muted-foreground">{report.reviewer_notes}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Methodology Traceability</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-6 text-muted-foreground">{report.methodology_trace}</p>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Evidence Sections</p>
          <h2 className="text-2xl font-semibold">{report.company} Validation Workspace</h2>
        </div>
        {report.sections.map((section) => (
          <Card key={section.id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="grid gap-1">
                  <CardTitle>{section.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{section.description}</p>
                </div>
                <Badge>{section.source_approval_status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="grid gap-3 md:grid-cols-3">
                <Score label="Coverage" value={section.coverage_score} />
                <Score label="Validation" value={section.openvals_validation_score} />
                <div className="grid gap-2">
                  <span className="text-xs font-semibold uppercase text-muted-foreground">
                    Required Sources
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {section.required_source_types.map((type) => (
                      <Badge key={type}>{type.replaceAll("_", " ")}</Badge>
                    ))}
                  </div>
                </div>
              </div>
              <p className="text-sm leading-6 text-muted-foreground">{section.methodology_trace}</p>
            </CardContent>
          </Card>
        ))}
        {report.sections.length === 0 ? (
          <p className="rounded-lg border border-border p-5 text-sm text-muted-foreground">
            No validation sections are available yet.
          </p>
        ) : null}
      </section>
    </div>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="grid gap-2">
      <span className="text-xs font-semibold uppercase text-muted-foreground">{label}</span>
      <strong className="text-2xl tabular-nums">{value.toFixed(1)}</strong>
      <Progress value={value} />
    </div>
  );
}
