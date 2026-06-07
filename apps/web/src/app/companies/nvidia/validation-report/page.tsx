import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchNvidiaValidationReport } from "@/lib/api";

export const metadata: Metadata = {
  title: "NVIDIA Validation Report | APIP",
  description: "OpenVals gold standard validation workspace for NVIDIA AI economics evidence."
};

export default async function NvidiaValidationReportPage() {
  const report = await fetchNvidiaValidationReport();
  return (
    <div className="grid gap-8">
      <header className="grid gap-4 border-b border-border pb-6">
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Gold Standard Validation</p>
          <Badge>{report.methodology_version}</Badge>
          <Badge>{report.status.replace("_", " ")}</Badge>
          {report.gold_standard_label ? <Badge>{report.gold_standard_label}</Badge> : null}
        </div>
        <div className="grid gap-2">
          <h1 className="text-4xl font-semibold">NVIDIA Validation Report</h1>
          <p className="max-w-3xl text-muted-foreground">
            Source-backed validation workspace for NVIDIA revenue, AI revenue, AI investment,
            infrastructure investment, earnings call evidence, and investor presentation evidence.
          </p>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          ["OpenVals Validation", `${report.openvals_validation_score.toFixed(1)}%`],
          ["Evidence Coverage", `${report.evidence_coverage_score.toFixed(1)}%`],
          ["Sections", String(report.sections.length)],
          ["Lineage Records", String(report.source_lineage.length)]
        ].map(([label, value]) => (
          <Card key={label}>
            <CardHeader>
              <p className="text-xs font-semibold uppercase text-muted-foreground">{label}</p>
              <CardTitle className="text-2xl">{value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Gold Standard Artifacts</p>
        <div className="flex flex-wrap gap-2">
          {[
            ["/companies/nvidia/evidence-timeline", "Evidence Timeline"],
            ["/companies/nvidia/source-lineage", "Source Lineage"],
            ["/companies/nvidia/openvals-score", "OpenVals Score"],
            ["/companies/nvidia/trust-report", "Trust Report"]
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
        {report.sections.map((section) => (
          <Card key={section.id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle>{section.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{section.description}</p>
                </div>
                <Badge>{section.source_approval_status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="grid gap-3 md:grid-cols-2">
                <Score label="Coverage" value={section.coverage_score} />
                <Score label="Validation" value={section.openvals_validation_score} />
              </div>
              <p className="text-sm leading-6 text-muted-foreground">{section.methodology_trace}</p>
              <div className="grid gap-2 text-sm text-muted-foreground">
                {section.evidence.map((evidence) => (
                  <a
                    className="rounded-md border border-border p-3 text-foreground underline-offset-4 hover:underline"
                    href={evidence.source.url ?? "#"}
                    key={evidence.id}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {evidence.source.title} · {evidence.approval_status}
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
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
