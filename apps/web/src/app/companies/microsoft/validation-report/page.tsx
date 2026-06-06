import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchMicrosoftValidationReport } from "@/lib/api";

export const metadata: Metadata = {
  title: "Microsoft Validation Report | APIP",
  description:
    "OpenVals gold standard validation workspace for Microsoft AI economics evidence."
};

export default async function MicrosoftValidationReportPage() {
  const report = await fetchMicrosoftValidationReport();
  const summary = [
    ["OpenVals Validation", `${report.openvals_validation_score.toFixed(1)}%`],
    ["Evidence Coverage", `${report.evidence_coverage_score.toFixed(1)}%`],
    ["Sections", String(report.sections.length)],
    ["Lineage Records", String(report.source_lineage.length)]
  ];

  return (
    <div className="grid gap-8">
      <header className="grid gap-4 border-b border-border pb-6">
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Gold Standard Validation</p>
          <Badge>{report.methodology_version}</Badge>
          <Badge>{report.status.replace("_", " ")}</Badge>
        </div>
        <div className="grid gap-2">
          <h1 className="text-4xl font-semibold">Microsoft Validation Report</h1>
          <p className="max-w-3xl text-muted-foreground">
            Source-backed validation workspace for Microsoft revenue, AI revenue, AI investment,
            infrastructure investment, earnings call evidence, and investor presentation evidence.
          </p>
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
        <p className="text-xs font-semibold uppercase text-muted-foreground">Pilot Artifacts</p>
        <div className="flex flex-wrap gap-2">
          {[
            ["/companies/microsoft/evidence-timeline", "Evidence Timeline"],
            ["/companies/microsoft/source-lineage", "Source Lineage"],
            ["/companies/microsoft/openvals-score", "OpenVals Score"],
            ["/companies/microsoft/trust-report", "Trust Report"]
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

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
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
          <h2 className="text-2xl font-semibold">Microsoft Validation Workspace</h2>
        </div>
        <div className="grid gap-4">
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
              <CardContent className="grid gap-5">
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
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[720px] text-left text-sm">
                    <thead className="border-b border-border text-xs uppercase text-muted-foreground">
                      <tr>
                        <th className="py-3 pr-3">Source</th>
                        <th className="py-3 pr-3">Type</th>
                        <th className="py-3 pr-3">Status</th>
                        <th className="py-3 pr-3">Credibility</th>
                        <th className="py-3 pr-3">Reviewer Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {section.evidence.map((evidence) => (
                        <tr key={evidence.id} className="border-b border-border/70">
                          <td className="py-3 pr-3">
                            {evidence.source.url ? (
                              <a
                                className="font-medium text-foreground underline-offset-4 hover:underline"
                                href={evidence.source.url}
                                rel="noreferrer"
                                target="_blank"
                              >
                                {evidence.source.title}
                              </a>
                            ) : (
                              <span className="font-medium">{evidence.source.title}</span>
                            )}
                            <p className="text-xs text-muted-foreground">{evidence.source.publisher}</p>
                          </td>
                          <td className="py-3 pr-3">{evidence.source.source_type.replaceAll("_", " ")}</td>
                          <td className="py-3 pr-3">{evidence.approval_status}</td>
                          <td className="py-3 pr-3 tabular-nums">
                            {evidence.source.credibility_score}
                          </td>
                          <td className="py-3 pr-3 text-muted-foreground">{evidence.reviewer_notes}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ))}
          {report.sections.length === 0 ? (
            <p className="rounded-lg border border-border p-5 text-sm text-muted-foreground">
              No Microsoft validation sections are available yet.
            </p>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="grid gap-2">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase text-muted-foreground">{label}</span>
        <span className="text-sm font-medium tabular-nums">{value.toFixed(1)}%</span>
      </div>
      <Progress value={value} />
    </div>
  );
}
