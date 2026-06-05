"use client";

import { Check, DatabaseZap, FileUp, Loader2, Lock, RotateCcw, X } from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type AdminItem = Record<string, string | number | null | undefined>;
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
type DashboardCounts = Record<string, number>;

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
  const [sourceMetrics, setSourceMetrics] = useState<SourceMetric[]>([]);
  const [lineage, setLineage] = useState<LineageRecord[]>([]);
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
    const [dashboard, metrics, lineageResponse, audits, ...resourceResponses] = await Promise.all([
      fetch("/api/admin/dashboard", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/source-metrics", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/lineage", { headers: authHeader }).then((response) => response.json()),
      fetch("/api/admin/audit-logs", { headers: authHeader }).then((response) => response.json()),
      ...resources.map((resource) =>
        fetch(`/api/admin/${resource.key}`, { headers: authHeader }).then((response) => response.json())
      )
    ]);
    setCounts(dashboard.counts ?? {});
    setSourceMetrics(metrics.items ?? []);
    setLineage(lineageResponse.items ?? []);
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

  async function action(path: string, success: string) {
    setBusy(true);
    try {
      await adminFetch(path, { method: "PATCH" });
      setMessage(success);
      await refreshAll();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally {
      setBusy(false);
    }
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
  onUpdate,
  resource
}: {
  busy: boolean;
  items: AdminItem[];
  onApproveSource: (id: string) => void;
  onRejectSource: (id: string) => void;
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
                <Button disabled={busy} onClick={() => onUpdate(String(item.id), { status: inactiveStatus })} size="sm" variant="outline">
                  {resource === "api-keys" ? "Revoke" : "Archive"}
                </Button>
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

function statusClass(status: string) {
  return cn(
    status === "approved" || status === "active"
      ? "border-emerald-500/50 text-emerald-300"
      : "",
    status === "rejected" || status === "archived" || status === "revoked"
      ? "border-red-500/50 text-red-300"
      : "",
    status === "pending" ? "border-amber-500/50 text-amber-300" : ""
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
