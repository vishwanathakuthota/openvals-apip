"use client";

import { Check, FileUp, Loader2, RotateCcw, ShieldCheck, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SourceMetric = {
  id: string;
  company: string;
  year: number;
  metric_type: string;
  value: number;
  source_url: string;
  source_type: string;
  confidence_score: number;
  created_by: string;
  approved_status: "pending" | "approved" | "rejected";
  last_updated?: string | null;
  methodology_note: string;
  source: {
    id: string;
    title: string;
    status: string;
    reliability_score: number;
    published_at?: string | null;
  };
};

type AuditLog = {
  id: string;
  actor?: string | null;
  action: string;
  target_type: string;
  target_id?: string | null;
  metadata: Record<string, string | number | null>;
  created_at?: string | null;
};

export function SourceManagement() {
  const [file, setFile] = useState<File | null>(null);
  const [metrics, setMetrics] = useState<SourceMetric[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [status, setStatus] = useState<string>("Ready");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const [metricsResponse, auditResponse] = await Promise.all([
      fetch("/api/admin/source-metrics", { cache: "no-store" }),
      fetch("/api/admin/audit-logs", { cache: "no-store" })
    ]);
    if (metricsResponse.ok) {
      const data = (await metricsResponse.json()) as { items: SourceMetric[] };
      setMetrics(data.items);
    }
    if (auditResponse.ok) {
      const data = (await auditResponse.json()) as { items: AuditLog[] };
      setAuditLogs(data.items);
    }
  }

  useEffect(() => {
    refresh().catch(() => setStatus("Backend unavailable"));
  }, []);

  async function uploadCsv() {
    if (!file) {
      setStatus("Select a CSV file");
      return;
    }
    setBusy(true);
    setStatus("Importing CSV");
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch("/api/admin/imports/csv", { method: "POST", body });
      const data = await response.json();
      if (!response.ok) {
        setStatus(data.detail?.message ?? data.message ?? "CSV import failed");
        return;
      }
      setFile(null);
      setStatus(`Imported ${data.imported_count} metric${data.imported_count === 1 ? "" : "s"}`);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function reviewMetric(metricId: string, action: "approve" | "reject") {
    setBusy(true);
    setStatus(`${action === "approve" ? "Approving" : "Rejecting"} source metric`);
    try {
      const response = await fetch(`/api/admin/source-metrics/${metricId}/${action}`, {
        method: "PATCH"
      });
      if (!response.ok) {
        const data = await response.json();
        setStatus(data.detail?.message ?? data.message ?? "Review action failed");
        return;
      }
      setStatus(action === "approve" ? "Metric published" : "Source rejected");
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-6">
      <section className="grid gap-4 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">CSV Import</p>
            <h2 className="text-xl font-semibold">Financial Metrics Upload</h2>
          </div>
          <Badge>{status}</Badge>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="flex min-h-10 flex-1 cursor-pointer items-center gap-3 rounded-md border border-border bg-background px-3 text-sm text-muted-foreground">
            <FileUp className="h-4 w-4" aria-hidden />
            <span className="truncate">{file?.name ?? "Select CSV file"}</span>
            <input
              accept=".csv,text/csv"
              className="sr-only"
              type="file"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <Button disabled={busy} onClick={uploadCsv}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <FileUp className="h-4 w-4" aria-hidden />}
            Upload
          </Button>
          <Button disabled={busy} onClick={refresh} variant="outline">
            <RotateCcw className="h-4 w-4" aria-hidden />
            Refresh
          </Button>
        </div>
      </section>

      <section className="grid gap-4 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">Source Review</p>
            <h2 className="text-xl font-semibold">Imported Metrics</h2>
          </div>
          <Badge>{metrics.length} records</Badge>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-border text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-3 pr-3 font-semibold">Company</th>
                <th className="py-3 pr-3 font-semibold">Metric</th>
                <th className="py-3 pr-3 font-semibold">Value</th>
                <th className="py-3 pr-3 font-semibold">Source</th>
                <th className="py-3 pr-3 font-semibold">Confidence</th>
                <th className="py-3 pr-3 font-semibold">Status</th>
                <th className="py-3 pr-3 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric) => (
                <tr className="border-b border-border/70 align-top" key={metric.id}>
                  <td className="py-3 pr-3">
                    <strong>{metric.company}</strong>
                    <span className="block text-xs text-muted-foreground">{metric.year}</span>
                  </td>
                  <td className="py-3 pr-3">{metric.metric_type.replaceAll("_", " ")}</td>
                  <td className="py-3 pr-3 tabular-nums">{metric.value.toLocaleString()}</td>
                  <td className="max-w-[260px] py-3 pr-3">
                    <a className="text-primary underline-offset-4 hover:underline" href={metric.source_url}>
                      {metric.source_type.replaceAll("_", " ")}
                    </a>
                    <span className="block truncate text-xs text-muted-foreground">
                      Reliability {metric.source.reliability_score}
                    </span>
                  </td>
                  <td className="py-3 pr-3">
                    <Badge>{metric.confidence_score.toFixed(1)}</Badge>
                  </td>
                  <td className="py-3 pr-3">
                    <Badge className={statusClass(metric.approved_status)}>
                      {metric.approved_status}
                    </Badge>
                  </td>
                  <td className="py-3 pr-3">
                    <div className="flex gap-2">
                      <Button
                        disabled={busy || metric.approved_status !== "pending"}
                        onClick={() => reviewMetric(metric.id, "approve")}
                        size="sm"
                      >
                        <Check className="h-4 w-4" aria-hidden />
                        Approve
                      </Button>
                      <Button
                        disabled={busy || metric.approved_status !== "pending"}
                        onClick={() => reviewMetric(metric.id, "reject")}
                        size="sm"
                        variant="outline"
                      >
                        <X className="h-4 w-4" aria-hidden />
                        Reject
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {!metrics.length ? (
                <tr>
                  <td className="py-6 text-muted-foreground" colSpan={7}>
                    No imported source metrics found.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-4 rounded-lg border border-border bg-card p-5">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Audit Logs</p>
          <h2 className="text-xl font-semibold">Source Workflow Activity</h2>
        </div>
        <div className="grid gap-2">
          {auditLogs.map((log) => (
            <article className="flex flex-wrap items-center gap-3 border-b border-border/70 py-3" key={log.id}>
              <ShieldCheck className="h-4 w-4 text-primary" aria-hidden />
              <span className="font-medium">{log.action.replaceAll("_", " ")}</span>
              <span className="text-sm text-muted-foreground">{log.actor ?? "System"}</span>
              <span className="text-xs text-muted-foreground">{formatDate(log.created_at)}</span>
            </article>
          ))}
          {!auditLogs.length ? <p className="text-sm text-muted-foreground">No audit events found.</p> : null}
        </div>
      </section>
    </div>
  );
}

function statusClass(status: SourceMetric["approved_status"]) {
  return cn(
    status === "approved" && "border-emerald-500/50 text-emerald-300",
    status === "rejected" && "border-red-500/50 text-red-300",
    status === "pending" && "border-amber-500/50 text-amber-300"
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
