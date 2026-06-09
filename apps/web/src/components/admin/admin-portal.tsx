"use client";

import { Check, DatabaseZap, FileUp, Loader2, Lock, RotateCcw, X } from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type AdminItem = Record<string, unknown>;
type SourceMetric = AdminItem & {
  id: string;
  company: string;
  year: number;
  metric_type: string;
  value: number;
  source_url: string;
  source_type: string;
  confidence_score: number;
  approved_status: "pending" | "approved" | "rejected";
};
type AuditLog = {
  id: string;
  actor?: string | null;
  action: string;
  target_type: string;
  created_at?: string | null;
};
type LineageRecord = {
  id: string;
  entity_type: string;
  entity_id: string;
  source_url: string;
  source_type: string;
  confidence_score: number;
  imported_by?: string | null;
  imported_at?: string | null;
  action: string;
};
type CompanyValidation = {
  id: string;
  company: string;
  status: string;
  openvals_validation_score: number;
  openvals_validation_label: string;
  evidence_coverage_score: number;
  confidence_score: number;
  evidence_count: number;
  reviewer_notes?: string | null;
  approved_at?: string | null;
};
type ResearchQueueItem = {
  id: string;
  company: string;
  status: string;
  status_key: string;
  priority: string;
  assigned_to?: string | null;
  reviewer?: string | null;
  progress_percent: number;
  evidence_coverage_score: number;
  evidence_count: number;
  notes?: string | null;
};
type ResearchProgress = {
  total_items: number;
  status_counts: Record<string, number>;
  assigned_items: number;
  unassigned_items: number;
  average_progress_percent: number;
  average_evidence_coverage_score: number;
  collected_evidence_count: number;
  approved_evidence_count: number;
};
type AutonomousEvidenceRecord = {
  id: string;
  company: string;
  metric: string;
  discovered_value: number;
  source_type: string;
  status: string;
  evidence_classification: string;
  confidence_score: number;
  confidence_label: string;
  evidence_coverage_score: number;
  openvals_score: number;
  openvals_classification: string;
  approval_recommendation?: string | null;
  reviewer?: string | null;
  reviewed_at?: string | null;
  approved_at?: string | null;
  published_at?: string | null;
};
type AutonomousDashboard = {
  workflow: string;
  auto_publish_enabled: boolean;
  research_queue: AutonomousEvidenceRecord[];
  validation_queue: AutonomousEvidenceRecord[];
  approval_queue: AutonomousEvidenceRecord[];
  publishing_queue: AutonomousEvidenceRecord[];
  evidence_timeline: AutonomousEvidenceRecord[];
  source_lineage: unknown[];
  trust_center: {
    total_records: number;
    published_records: number;
    approved_records: number;
    under_review_records: number;
    manual_review_required: number;
    average_confidence: number;
    average_openvals_score: number;
    public_lineage_records: number;
  };
};
type DashboardCounts = Record<string, number>;
type CommercialDashboard = {
  revenue: {
    monthly_recurring_revenue: number;
    draft_invoice_amount: number;
    invoice_count: number;
  };
  active_users: {
    active_api_keys: number;
    active_subscriptions: number;
  };
  api_consumption: {
    requests_today: number;
    total_requests: number;
    top_endpoints: { endpoint: string; request_count: number }[];
  };
  plan_distribution: Record<string, number>;
};
type LaunchMetrics = {
  signups: number;
  enterprise_inquiries: number;
  api_keys_created: number;
  api_usage: {
    requests_today: number;
    total_requests: number;
    top_endpoints: { endpoint: string; request_count: number }[];
  };
  top_endpoints: { endpoint: string; request_count: number }[];
  active_plans: Record<string, number>;
};

const resources = [
  { key: "companies", label: "Companies", fields: ["name", "ticker", "website_url", "status"] },
  { key: "industries", label: "Industries", fields: ["name", "status"] },
  { key: "countries", label: "Countries", fields: ["name", "iso_code", "region"] },
  { key: "models", label: "Models", fields: ["name", "model_family", "status"] },
  { key: "sources", label: "Sources", fields: ["title", "source_type", "url", "publisher", "status"] },
  { key: "api-keys", label: "API Keys", fields: ["name", "plan"] }
] as const;

export function AdminPortal() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("admin@openvalidations.com");
  const [password, setPassword] = useState("");
  const [active, setActive] = useState<(typeof resources)[number]["key"]>("companies");
  const [items, setItems] = useState<Record<string, AdminItem[]>>({});
  const [counts, setCounts] = useState<DashboardCounts>({});
  const [commercialDashboard, setCommercialDashboard] = useState<CommercialDashboard | null>(null);
  const [launchMetrics, setLaunchMetrics] = useState<LaunchMetrics | null>(null);
  const [sourceMetrics, setSourceMetrics] = useState<SourceMetric[]>([]);
  const [lineage, setLineage] = useState<LineageRecord[]>([]);
  const [companyValidations, setCompanyValidations] = useState<CompanyValidation[]>([]);
  const [researchQueue, setResearchQueue] = useState<ResearchQueueItem[]>([]);
  const [researchProgress, setResearchProgress] = useState<ResearchProgress | null>(null);
  const [autonomousDashboard, setAutonomousDashboard] = useState<AutonomousDashboard | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [form, setForm] = useState<Record<string, string>>({});
  const [file, setFile] = useState<File | null>(null);
  const [catalogFile, setCatalogFile] = useState<File | null>(null);
  const [catalogImportType, setCatalogImportType] = useState("companies");
  const [message, setMessage] = useState("Admin login required");
  const [busy, setBusy] = useState(false);
  const config = useMemo(() => resources.find((resource) => resource.key === active), [active]);

  useEffect(() => {
    const stored = sessionStorage.getItem("apip_admin_token");
    if (stored) {
      setToken(stored);
      setMessage("Admin session restored");
    }
  }, []);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("Signing in");
    try {
      const response = await fetch("/api/admin/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (!response.ok || data.user?.role !== "admin") {
        setMessage("Admin credentials are required");
        return;
      }
      sessionStorage.setItem("apip_admin_token", data.access_token);
      setToken(data.access_token);
      setMessage(`Signed in as ${data.user.email}`);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    sessionStorage.removeItem("apip_admin_token");
    setToken(null);
    setItems({});
    setMessage("Signed out");
  }

  async function adminFetch(path: string, init: RequestInit = {}) {
    const response = await fetch(`/api/admin/${path}`, {
      ...init,
      headers: {
        ...(init.headers ?? {}),
        Authorization: `Bearer ${token}`
      }
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail?.message ?? data.message ?? "Admin request failed");
    }
    return response.json();
  }

  const refreshAll = useCallback(async (currentToken = token) => {
    if (!currentToken) {
      return;
    }
    const authHeader = { Authorization: `Bearer ${currentToken}` };
    const [
      dashboard,
      launchMetricsResponse,
      metrics,
      lineageResponse,
      validationsResponse,
      researchQueueResponse,
      researchProgressResponse,
      autonomousResponse,
      audits,
      ...resourceResponses
    ] = await Promise.all([
      fetch("/api/admin/dashboard", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/launch-metrics", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/source-metrics", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/lineage", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/company-validations", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/research-queue", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/research-progress", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/autonomous-research", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/audit-logs", { headers: authHeader }).then((response) => response.json()),
      ...resources.map((resource) =>
        fetch(`/api/admin/${resource.key}`, { headers: authHeader }).then((response) => response.json())
      )
    ]);
    setCounts(dashboard.counts ?? {});
    setCommercialDashboard(dashboard.commercial ?? null);
    setLaunchMetrics(launchMetricsResponse ?? dashboard.post_launch ?? null);
    setSourceMetrics(metrics.items ?? []);
    setLineage(lineageResponse.items ?? []);
    setCompanyValidations(validationsResponse.items ?? []);
    setResearchQueue(researchQueueResponse.items ?? []);
    setResearchProgress(researchProgressResponse ?? null);
    setAutonomousDashboard(autonomousResponse ?? null);
    setAuditLogs(audits.items ?? []);
    setItems(Object.fromEntries(resources.map((resource, index) => [resource.key, resourceResponses[index].items ?? []])));
  }, [token]);

  useEffect(() => {
    if (token) {
      refreshAll(token).catch(() => setMessage("Unable to load admin data"));
    }
  }, [refreshAll, token]);

  async function createItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!config) {
      return;
    }
    setBusy(true);
    try {
      const data = await adminFetch(config.key, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      setForm({});
      setMessage(data.api_key ? `Created API key: ${data.api_key}` : `${config.label} updated`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function updateItem(resource: string, id: string, payload: Record<string, string>) {
    setBusy(true);
    try {
      await adminFetch(`${resource}/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      setMessage(`${resource} saved`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Update failed");
    } finally {
      setBusy(false);
    }
  }

  async function action(path: string, success: string, method = "PATCH") {
    setBusy(true);
    try {
      await adminFetch(path, { method });
      setMessage(success);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  async function rotateApiKey(id: string) {
    setBusy(true);
    try {
      const data = await adminFetch(`api-keys/${id}/rotate`, { method: "POST" });
      setMessage(`Rotated API key: ${data.api_key}`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "API key rotation failed");
    } finally {
      setBusy(false);
    }
  }

  async function revokeApiKey(id: string) {
    await action(`api-keys/${id}/revoke`, "API key revoked", "POST");
  }

  async function uploadCsv() {
    if (!file) {
      setMessage("Select a CSV file");
      return;
    }
    setBusy(true);
    const body = new FormData();
    body.append("file", file);
    try {
      const data = await adminFetch("imports/csv", { method: "POST", body });
      setFile(null);
      setMessage(`Imported ${data.imported_count} metrics`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "CSV import failed");
    } finally {
      setBusy(false);
    }
  }

  async function uploadCatalogCsv() {
    if (!catalogFile) {
      setMessage("Select a catalog CSV file");
      return;
    }
    setBusy(true);
    const body = new FormData();
    body.append("file", catalogFile);
    try {
      const data = await adminFetch(`imports/catalog/${catalogImportType}/csv`, { method: "POST", body });
      setCatalogFile(null);
      setMessage(`Imported ${data.imported_count} ${data.entity_type}`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Catalog import failed");
    } finally {
      setBusy(false);
    }
  }

  async function triggerSeedImport() {
    setBusy(true);
    try {
      await adminFetch("seed-import", { method: "POST" });
      setMessage("Seed import completed");
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Seed import failed");
    } finally {
      setBusy(false);
    }
  }

  async function updateResearchStatus(id: string, status: string) {
    setBusy(true);
    try {
      await adminFetch(`research-queue/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
      });
      setMessage(`Research status moved to ${status.replaceAll("_", " ")}`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Research status update failed");
    } finally {
      setBusy(false);
    }
  }

  async function assignResearchToMe(id: string) {
    setBusy(true);
    try {
      await adminFetch(`research-queue/${id}/assign`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes: "Assigned from admin research operations dashboard." })
      });
      setMessage("Research assigned");
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Research assignment failed");
    } finally {
      setBusy(false);
    }
  }

  async function runAutonomousAgent(agentName: string) {
    setBusy(true);
    try {
      await adminFetch(`autonomous-research/run/${agentName}`, { method: "POST" });
      setMessage(`${agentName.replaceAll("_", " ")} agent run completed`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Agent run failed");
    } finally {
      setBusy(false);
    }
  }

  async function reviewAutonomousEvidence(id: string, decision: string) {
    setBusy(true);
    try {
      await adminFetch(`autonomous-research/evidence/${id}/review`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          notes: `Reviewer selected ${decision.replaceAll("_", " ")} from Autonomous Research dashboard.`
        })
      });
      setMessage(`Evidence ${decision.replaceAll("_", " ")}`);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Evidence review failed");
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <section className="mx-auto grid max-w-md gap-5 rounded-lg border border-border bg-card p-6">
        <div className="grid gap-2">
          <Lock className="h-5 w-5 text-primary" aria-hidden />
          <h2 className="text-2xl font-semibold">Admin Login</h2>
          <p className="text-sm text-muted-foreground">Administrative controls require an admin JWT session.</p>
        </div>
        <form className="grid gap-3" onSubmit={login}>
          <input
            className="h-10 rounded-md border border-border bg-background px-3 text-sm"
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            type="email"
            value={email}
          />
          <input
            className="h-10 rounded-md border border-border bg-background px-3 text-sm"
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            type="password"
            value={password}
          />
          <Button disabled={busy} type="submit">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <Lock className="h-4 w-4" aria-hidden />}
            Sign In
          </Button>
        </form>
        <Badge>{message}</Badge>
      </section>
    );
  }

  return (
    <div className="grid gap-6">
      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">Admin Dashboard</p>
            <h2 className="text-2xl font-semibold">Operations Control</h2>
          </div>
          <div className="flex gap-2">
            <Button disabled={busy} onClick={() => refreshAll()} variant="outline">
              <RotateCcw className="h-4 w-4" aria-hidden />
              Refresh
            </Button>
            <Button onClick={logout} variant="outline">
              <Lock className="h-4 w-4" aria-hidden />
              Sign Out
            </Button>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-4 xl:grid-cols-7">
          {Object.entries(counts).map(([key, value]) => (
            <div className="rounded-md border border-border bg-background p-3" key={key}>
              <span className="text-xs text-muted-foreground">{key.replaceAll("_", " ")}</span>
              <strong className="block text-xl">{value}</strong>
            </div>
          ))}
        </div>
        <CommercialDashboardCards dashboard={commercialDashboard} />
        <LaunchMetricsCards metrics={launchMetrics} />
        <Badge>{message}</Badge>
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap gap-2">
          {resources.map((resource) => (
            <Button
              key={resource.key}
              onClick={() => setActive(resource.key)}
              variant={active === resource.key ? "default" : "outline"}
            >
              {resource.label}
            </Button>
          ))}
        </div>
        {config ? (
          <>
            <form className="grid gap-3 md:grid-cols-3 xl:grid-cols-5" onSubmit={createItem}>
              {config.fields.map((field) => (
                <input
                  className="h-10 rounded-md border border-border bg-background px-3 text-sm"
                  key={field}
                  onChange={(event) => setForm((current) => ({ ...current, [field]: event.target.value }))}
                  placeholder={field.replaceAll("_", " ")}
                  value={form[field] ?? ""}
                />
              ))}
              <Button disabled={busy} type="submit">
                Add {config.label}
              </Button>
            </form>
            <AdminTable
              busy={busy}
              items={items[config.key] ?? []}
              onApproveSource={(id) => action(`sources/${id}/approve`, "Source approved")}
              onRejectSource={(id) => action(`sources/${id}/reject`, "Source rejected")}
              onRevokeApiKey={revokeApiKey}
              onRotateApiKey={rotateApiKey}
              onUpdate={(id, payload) => updateItem(config.key, id, payload)}
              resource={config.key}
            />
          </>
        ) : null}
      </section>

      <section className="grid gap-4 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">ETL</p>
            <h2 className="text-xl font-semibold">Imports and Review</h2>
          </div>
          <Button disabled={busy} onClick={triggerSeedImport} variant="outline">
            <DatabaseZap className="h-4 w-4" aria-hidden />
            Trigger Seed Import
          </Button>
        </div>
        <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto]">
          <label className="flex min-h-10 flex-1 cursor-pointer items-center gap-3 rounded-md border border-border bg-background px-3 text-sm text-muted-foreground">
            <FileUp className="h-4 w-4" aria-hidden />
            <span className="truncate">{file?.name ?? "Select financial metrics CSV"}</span>
            <input
              accept=".csv,text/csv"
              className="sr-only"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              type="file"
            />
          </label>
          <Button disabled={busy} onClick={uploadCsv}>
            <FileUp className="h-4 w-4" aria-hidden />
            Upload Metrics
          </Button>
        </div>
        <div className="grid gap-3 md:grid-cols-[180px_minmax(0,1fr)_auto]">
          <select
            className="h-10 rounded-md border border-border bg-background px-3 text-sm"
            onChange={(event) => setCatalogImportType(event.target.value)}
            value={catalogImportType}
          >
            <option value="companies">Companies</option>
            <option value="industries">Industries</option>
            <option value="countries">Countries</option>
            <option value="models">Models</option>
          </select>
          <label className="flex min-h-10 cursor-pointer items-center gap-3 rounded-md border border-border bg-background px-3 text-sm text-muted-foreground">
            <FileUp className="h-4 w-4" aria-hidden />
            <span className="truncate">{catalogFile?.name ?? "Select catalog CSV"}</span>
            <input
              accept=".csv,text/csv"
              className="sr-only"
              onChange={(event) => setCatalogFile(event.target.files?.[0] ?? null)}
              type="file"
            />
          </label>
          <Button disabled={busy} onClick={uploadCatalogCsv}>
            <FileUp className="h-4 w-4" aria-hidden />
            Upload Catalog
          </Button>
        </div>
        <ImportedMetricsTable
          busy={busy}
          items={sourceMetrics}
          onApprove={(id) => action(`source-metrics/${id}/approve`, "Metric approved")}
          onReject={(id) => action(`source-metrics/${id}/reject`, "Metric rejected")}
        />
        <DataLineageTable items={lineage} />
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Research Operations</p>
          <h2 className="text-xl font-semibold">Research Queue</h2>
        </div>
        <ResearchProgressCards progress={researchProgress} />
        <ResearchQueueTable
          busy={busy}
          items={researchQueue}
          onAssign={assignResearchToMe}
          onStatus={updateResearchStatus}
        />
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">Autonomous Research Operations</p>
            <h2 className="text-xl font-semibold">Trust Workflow Queues</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {["research", "validation", "approval", "publisher"].map((agentName) => (
              <Button disabled={busy} key={agentName} onClick={() => runAutonomousAgent(agentName)} size="sm" variant="outline">
                Run {agentName}
              </Button>
            ))}
          </div>
        </div>
        <AutonomousDashboardView
          busy={busy}
          dashboard={autonomousDashboard}
          onReview={reviewAutonomousEvidence}
          onRunPublisher={() => runAutonomousAgent("publisher")}
        />
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">OpenVals Validation</p>
          <h2 className="text-xl font-semibold">Company Validation Dashboard</h2>
        </div>
        <CompanyValidationTable
          busy={busy}
          items={companyValidations}
          onApprove={(id) => action(`company-validations/${id}/approve`, "Company validation approved")}
          onReject={(id) => action(`company-validations/${id}/reject`, "Company validation rejected")}
        />
      </section>

      <section className="grid gap-3 rounded-lg border border-border bg-card p-5">
        <h2 className="text-xl font-semibold">Audit Logs</h2>
        <div className="grid gap-2">
          {auditLogs.map((log) => (
            <article className="flex flex-wrap gap-3 border-b border-border/70 py-2" key={log.id}>
              <strong>{log.action.replaceAll("_", " ")}</strong>
              <span className="text-sm text-muted-foreground">{log.actor ?? "System"}</span>
              <span className="text-xs text-muted-foreground">{formatDate(log.created_at)}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function AdminTable({
  busy,
  items,
  onApproveSource,
  onRejectSource,
  onRevokeApiKey,
  onRotateApiKey,
  onUpdate,
  resource
}: {
  busy: boolean;
  items: AdminItem[];
  onApproveSource: (id: string) => void;
  onRejectSource: (id: string) => void;
  onRevokeApiKey: (id: string) => void;
  onRotateApiKey: (id: string) => void;
  onUpdate: (id: string, payload: Record<string, string>) => void;
  resource: string;
}) {
  const inactiveStatus = resource === "api-keys" ? "revoked" : "archived";
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[820px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Name / Title</th>
            <th className="py-3 pr-3">Slug / Type</th>
            <th className="py-3 pr-3">Status</th>
            <th className="py-3 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr className="border-b border-border/70" key={String(item.id)}>
              <td className="py-3 pr-3">{String(item.name ?? item.title ?? item.id)}</td>
              <td className="py-3 pr-3">
                {String(item.slug ?? item.source_type ?? item.model_family ?? item.key_prefix ?? "")}
              </td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(String(item.status ?? ""))}>{String(item.status ?? "active")}</Badge>
              </td>
              <td className="flex flex-wrap gap-2 py-3 pr-3">
                <Button disabled={busy} onClick={() => onUpdate(String(item.id), { status: "active" })} size="sm">
                  Active
                </Button>
                {resource !== "api-keys" ? (
                  <Button disabled={busy} onClick={() => onUpdate(String(item.id), { status: inactiveStatus })} size="sm" variant="outline">
                    Archive
                  </Button>
                ) : null}
                {resource === "api-keys" ? (
                  <>
                    <Button disabled={busy} onClick={() => onRotateApiKey(String(item.id))} size="sm" variant="outline">
                      Rotate
                    </Button>
                    <Button disabled={busy} onClick={() => onRevokeApiKey(String(item.id))} size="sm" variant="outline">
                      Revoke Now
                    </Button>
                  </>
                ) : null}
                {resource === "sources" ? (
                  <>
                    <Button disabled={busy} onClick={() => onApproveSource(String(item.id))} size="sm">
                      <Check className="h-4 w-4" aria-hidden />
                      Approve
                    </Button>
                    <Button disabled={busy} onClick={() => onRejectSource(String(item.id))} size="sm" variant="outline">
                      <X className="h-4 w-4" aria-hidden />
                      Reject
                    </Button>
                  </>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CommercialDashboardCards({ dashboard }: { dashboard: CommercialDashboard | null }) {
  if (!dashboard) {
    return null;
  }
  const cards = [
    {
      label: "Monthly recurring revenue",
      value: `$${dashboard.revenue.monthly_recurring_revenue.toLocaleString()}`
    },
    {
      label: "Draft invoices",
      value: `$${dashboard.revenue.draft_invoice_amount.toLocaleString()}`
    },
    {
      label: "Active API keys",
      value: dashboard.active_users.active_api_keys.toLocaleString()
    },
    {
      label: "Requests today",
      value: dashboard.api_consumption.requests_today.toLocaleString()
    }
  ];
  return (
    <div className="grid gap-3 md:grid-cols-4">
      {cards.map((card) => (
        <div className="rounded-md border border-border bg-background p-3" key={card.label}>
          <span className="text-xs text-muted-foreground">{card.label}</span>
          <strong className="block text-xl">{card.value}</strong>
        </div>
      ))}
      <div className="grid gap-2 rounded-md border border-border bg-background p-3 md:col-span-4">
        <span className="text-xs text-muted-foreground">Plan distribution</span>
        <div className="flex flex-wrap gap-2">
          {Object.entries(dashboard.plan_distribution).map(([plan, count]) => (
            <Badge key={plan}>
              {plan}: {count}
            </Badge>
          ))}
        </div>
      </div>
    </div>
  );
}

function LaunchMetricsCards({ metrics }: { metrics: LaunchMetrics | null }) {
  if (!metrics) {
    return null;
  }
  const cards = [
    { label: "Beta signups", value: metrics.signups.toLocaleString() },
    { label: "Enterprise inquiries", value: metrics.enterprise_inquiries.toLocaleString() },
    { label: "API keys created", value: metrics.api_keys_created.toLocaleString() },
    { label: "Total API usage", value: metrics.api_usage.total_requests.toLocaleString() }
  ];
  return (
    <div className="grid gap-3 rounded-md border border-border bg-background p-3">
      <div>
        <span className="text-xs font-semibold uppercase text-muted-foreground">Post-launch metrics</span>
        <strong className="block text-lg">Public Beta Funnel</strong>
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        {cards.map((card) => (
          <div className="rounded-md border border-border bg-card p-3" key={card.label}>
            <span className="text-xs text-muted-foreground">{card.label}</span>
            <strong className="block text-xl">{card.value}</strong>
          </div>
        ))}
      </div>
      <div className="grid gap-3 lg:grid-cols-2">
        <div className="grid gap-2">
          <span className="text-xs text-muted-foreground">Top endpoints</span>
          <div className="flex flex-wrap gap-2">
            {metrics.top_endpoints.length ? (
              metrics.top_endpoints.map((endpoint) => (
                <Badge key={endpoint.endpoint}>
                  {endpoint.endpoint}: {endpoint.request_count}
                </Badge>
              ))
            ) : (
              <Badge>No usage yet</Badge>
            )}
          </div>
        </div>
        <div className="grid gap-2">
          <span className="text-xs text-muted-foreground">Active plans</span>
          <div className="flex flex-wrap gap-2">
            {Object.entries(metrics.active_plans).map(([plan, count]) => (
              <Badge key={plan}>
                {plan}: {count}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ImportedMetricsTable({
  busy,
  items,
  onApprove,
  onReject
}: {
  busy: boolean;
  items: SourceMetric[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[900px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Company</th>
            <th className="py-3 pr-3">Metric</th>
            <th className="py-3 pr-3">Value</th>
            <th className="py-3 pr-3">Confidence</th>
            <th className="py-3 pr-3">Status</th>
            <th className="py-3 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((metric) => (
            <tr className="border-b border-border/70" key={metric.id}>
              <td className="py-3 pr-3">{metric.company}</td>
              <td className="py-3 pr-3">{metric.metric_type.replaceAll("_", " ")}</td>
              <td className="py-3 pr-3 tabular-nums">{metric.value.toLocaleString()}</td>
              <td className="py-3 pr-3">{metric.confidence_score.toFixed(1)}</td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(metric.approved_status)}>{metric.approved_status}</Badge>
              </td>
              <td className="flex gap-2 py-3 pr-3">
                <Button disabled={busy || metric.approved_status !== "pending"} onClick={() => onApprove(metric.id)} size="sm">
                  Approve
                </Button>
                <Button disabled={busy || metric.approved_status !== "pending"} onClick={() => onReject(metric.id)} size="sm" variant="outline">
                  Reject
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DataLineageTable({ items }: { items: LineageRecord[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[980px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Entity</th>
            <th className="py-3 pr-3">Source</th>
            <th className="py-3 pr-3">Confidence</th>
            <th className="py-3 pr-3">Imported By</th>
            <th className="py-3 pr-3">Imported Date</th>
            <th className="py-3 pr-3">Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((record) => (
            <tr className="border-b border-border/70" key={record.id}>
              <td className="py-3 pr-3">{record.entity_type.replaceAll("_", " ")}</td>
              <td className="max-w-[320px] py-3 pr-3">
                <a className="truncate text-primary underline-offset-4 hover:underline" href={record.source_url}>
                  {record.source_type.replaceAll("_", " ")}
                </a>
              </td>
              <td className="py-3 pr-3 tabular-nums">{record.confidence_score.toFixed(1)}</td>
              <td className="py-3 pr-3">{record.imported_by ?? "Admin"}</td>
              <td className="py-3 pr-3">{formatDate(record.imported_at)}</td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(record.action)}>{record.action}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 ? <p className="py-3 text-sm text-muted-foreground">No catalog lineage records yet.</p> : null}
    </div>
  );
}

function ResearchProgressCards({ progress }: { progress: ResearchProgress | null }) {
  if (!progress) {
    return <p className="text-sm text-muted-foreground">Research progress metrics are loading.</p>;
  }
  const cards = [
    ["Total", progress.total_items],
    ["Assigned", progress.assigned_items],
    ["Unassigned", progress.unassigned_items],
    ["Avg Progress", `${progress.average_progress_percent.toFixed(1)}%`],
    ["Avg Coverage", progress.average_evidence_coverage_score.toFixed(1)],
    ["Evidence", progress.collected_evidence_count],
    ["Approved Evidence", progress.approved_evidence_count]
  ];
  return (
    <div className="grid gap-3 md:grid-cols-4 xl:grid-cols-7">
      {cards.map(([label, value]) => (
        <div className="rounded-md border border-border bg-background p-3" key={String(label)}>
          <span className="text-xs text-muted-foreground">{label}</span>
          <strong className="block text-xl">{value}</strong>
        </div>
      ))}
    </div>
  );
}

function ResearchQueueTable({
  busy,
  items,
  onAssign,
  onStatus
}: {
  busy: boolean;
  items: ResearchQueueItem[];
  onAssign: (id: string) => void;
  onStatus: (id: string, status: string) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1080px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Company</th>
            <th className="py-3 pr-3">Status</th>
            <th className="py-3 pr-3">Assigned</th>
            <th className="py-3 pr-3">Reviewer</th>
            <th className="py-3 pr-3">Coverage</th>
            <th className="py-3 pr-3">Progress</th>
            <th className="py-3 pr-3">Evidence</th>
            <th className="py-3 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr className="border-b border-border/70" key={item.id}>
              <td className="py-3 pr-3">{item.company}</td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(item.status_key)}>{item.status}</Badge>
              </td>
              <td className="py-3 pr-3">{item.assigned_to ?? "Unassigned"}</td>
              <td className="py-3 pr-3">{item.reviewer ?? "Unassigned"}</td>
              <td className="py-3 pr-3 tabular-nums">{item.evidence_coverage_score.toFixed(1)}</td>
              <td className="py-3 pr-3 tabular-nums">{item.progress_percent.toFixed(1)}%</td>
              <td className="py-3 pr-3">{item.evidence_count}</td>
              <td className="flex flex-wrap gap-2 py-3 pr-3">
                <Button disabled={busy} onClick={() => onAssign(item.id)} size="sm" variant="outline">
                  Assign
                </Button>
                <Button disabled={busy} onClick={() => onStatus(item.id, "researching")} size="sm" variant="outline">
                  Researching
                </Button>
                <Button disabled={busy} onClick={() => onStatus(item.id, "under_review")} size="sm" variant="outline">
                  Review
                </Button>
                <Button disabled={busy} onClick={() => onStatus(item.id, "published")} size="sm">
                  Publish
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 ? <p className="py-3 text-sm text-muted-foreground">No research queue items yet.</p> : null}
    </div>
  );
}

function AutonomousDashboardView({
  busy,
  dashboard,
  onReview,
  onRunPublisher
}: {
  busy: boolean;
  dashboard: AutonomousDashboard | null;
  onReview: (id: string, decision: string) => void;
  onRunPublisher: () => void;
}) {
  if (!dashboard) {
    return <p className="text-sm text-muted-foreground">Autonomous research queues are loading.</p>;
  }
  const metrics = [
    ["Records", dashboard.trust_center.total_records],
    ["Under Review", dashboard.trust_center.under_review_records],
    ["Manual Review", dashboard.trust_center.manual_review_required],
    ["Approved", dashboard.trust_center.approved_records],
    ["Published", dashboard.trust_center.published_records],
    ["Avg Confidence", dashboard.trust_center.average_confidence.toFixed(1)],
    ["Avg OpenVals", dashboard.trust_center.average_openvals_score.toFixed(1)]
  ];
  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap gap-2">
        {dashboard.workflow.split(" -> ").map((step) => (
          <Badge key={step}>{step}</Badge>
        ))}
        <Badge className="border-emerald-500/50 text-emerald-300">
          Auto publish: {dashboard.auto_publish_enabled ? "on" : "off"}
        </Badge>
      </div>
      <div className="grid gap-3 md:grid-cols-4 xl:grid-cols-7">
        {metrics.map(([label, value]) => (
          <div className="rounded-md border border-border bg-background p-3" key={String(label)}>
            <span className="text-xs text-muted-foreground">{label}</span>
            <strong className="block text-xl">{value}</strong>
          </div>
        ))}
      </div>
      <AutonomousQueueTable
        busy={busy}
        items={dashboard.approval_queue}
        onReview={onReview}
        queueName="Approval Queue"
      />
      <AutonomousQueueTable
        busy={busy}
        items={dashboard.publishing_queue}
        onReview={onReview}
        onRunPublisher={onRunPublisher}
        queueName="Publishing Queue"
      />
      <AutonomousQueueTable
        busy={busy}
        items={dashboard.evidence_timeline.slice(0, 12)}
        onReview={onReview}
        queueName="Evidence Timeline"
      />
      <p className="text-sm text-muted-foreground">
        Source lineage explorer records: {dashboard.source_lineage.length}. Public lineage appears only after approved
        evidence is published.
      </p>
    </div>
  );
}

function AutonomousQueueTable({
  busy,
  items,
  onReview,
  onRunPublisher,
  queueName
}: {
  busy: boolean;
  items: AutonomousEvidenceRecord[];
  onReview: (id: string, decision: string) => void;
  onRunPublisher?: () => void;
  queueName: string;
}) {
  return (
    <div className="overflow-x-auto">
      <div className="mb-2 flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold">{queueName}</h3>
        {onRunPublisher ? (
          <Button disabled={busy || items.length === 0} onClick={onRunPublisher} size="sm">
            Publish Approved
          </Button>
        ) : null}
      </div>
      <table className="w-full min-w-[1120px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Company</th>
            <th className="py-3 pr-3">Metric</th>
            <th className="py-3 pr-3">Class</th>
            <th className="py-3 pr-3">Status</th>
            <th className="py-3 pr-3">Confidence</th>
            <th className="py-3 pr-3">Coverage</th>
            <th className="py-3 pr-3">OpenVals</th>
            <th className="py-3 pr-3">Recommendation</th>
            <th className="py-3 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr className="border-b border-border/70" key={item.id}>
              <td className="py-3 pr-3">{item.company}</td>
              <td className="py-3 pr-3">{item.metric.replaceAll("_", " ")}</td>
              <td className="py-3 pr-3">
                <Badge>{item.evidence_classification}</Badge>
              </td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(item.status.toLowerCase().replaceAll(" ", "_"))}>
                  {item.status}
                </Badge>
              </td>
              <td className="py-3 pr-3 tabular-nums">{item.confidence_score.toFixed(1)}</td>
              <td className="py-3 pr-3 tabular-nums">{item.evidence_coverage_score.toFixed(1)}%</td>
              <td className="py-3 pr-3">
                <span className="tabular-nums">{item.openvals_score.toFixed(1)}</span>
                <span className="ml-2 text-xs text-muted-foreground">{item.openvals_classification}</span>
              </td>
              <td className="py-3 pr-3">{item.approval_recommendation ?? "n/a"}</td>
              <td className="flex flex-wrap gap-2 py-3 pr-3">
                <Button disabled={busy || item.status !== "Under Review"} onClick={() => onReview(item.id, "approve")} size="sm">
                  Approve
                </Button>
                <Button disabled={busy || item.status !== "Under Review"} onClick={() => onReview(item.id, "request_additional_evidence")} size="sm" variant="outline">
                  More Evidence
                </Button>
                <Button disabled={busy || item.status !== "Under Review"} onClick={() => onReview(item.id, "reject")} size="sm" variant="outline">
                  Reject
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 ? <p className="py-3 text-sm text-muted-foreground">No records in {queueName.toLowerCase()}.</p> : null}
    </div>
  );
}

function CompanyValidationTable({
  busy,
  items,
  onApprove,
  onReject
}: {
  busy: boolean;
  items: CompanyValidation[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[980px] text-left text-sm">
        <thead className="border-b border-border text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-3">Company</th>
            <th className="py-3 pr-3">Validation</th>
            <th className="py-3 pr-3">Coverage</th>
            <th className="py-3 pr-3">Confidence</th>
            <th className="py-3 pr-3">Evidence</th>
            <th className="py-3 pr-3">Status</th>
            <th className="py-3 pr-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr className="border-b border-border/70" key={item.id}>
              <td className="py-3 pr-3">{item.company}</td>
              <td className="py-3 pr-3">
                <strong className="tabular-nums">{item.openvals_validation_score.toFixed(1)}</strong>
                <span className="ml-2 text-xs text-muted-foreground">{item.openvals_validation_label}</span>
              </td>
              <td className="py-3 pr-3 tabular-nums">{item.evidence_coverage_score.toFixed(1)}</td>
              <td className="py-3 pr-3 tabular-nums">{item.confidence_score.toFixed(1)}</td>
              <td className="py-3 pr-3">{item.evidence_count}</td>
              <td className="py-3 pr-3">
                <Badge className={statusClass(item.status)}>{item.status.replaceAll("_", " ")}</Badge>
              </td>
              <td className="flex gap-2 py-3 pr-3">
                <Button disabled={busy || item.status === "approved"} onClick={() => onApprove(item.id)} size="sm">
                  Approve
                </Button>
                <Button disabled={busy || item.status === "rejected"} onClick={() => onReject(item.id)} size="sm" variant="outline">
                  Reject
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 ? <p className="py-3 text-sm text-muted-foreground">No company validations yet.</p> : null}
    </div>
  );
}

function statusClass(status: string) {
  return cn(
    status === "approved" || status === "active" || status === "published"
      ? "border-emerald-500/50 text-emerald-300"
      : "",
    status === "rejected" || status === "archived" || status === "revoked"
      ? "border-red-500/50 text-red-300"
      : "",
    status === "pending" ||
      status === "not_started" ||
      status === "researching" ||
      status === "evidence_collected" ||
      status === "under_review"
      ? "border-amber-500/50 text-amber-300"
      : ""
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
