"use client";

import { DatabaseZap, Loader2, Lock, Play } from "lucide-react";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

type IngestionStatus = {
  enabled: boolean;
  yahoo_finance_enabled: boolean;
  sec_edgar_enabled: boolean;
  interval_minutes: number;
  scheduler_task: string;
  last_run?: {
    id: string;
    status: string;
    started_at?: string | null;
    completed_at?: string | null;
    records_created: number;
    records_failed: number;
    message?: string | null;
  } | null;
  recent_records: Array<{
    id: string;
    company_slug: string;
    symbol?: string | null;
    metric_type: string;
    value?: number | null;
    source_type: string;
    retrieved_at: string;
    freshness_score: number;
    confidence_score: number;
    ingestion_status: string;
  }>;
};

export default function AdminIngestionPage() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("admin@openvalidations.com");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<IngestionStatus | null>(null);
  const [message, setMessage] = useState("Admin login required");
  const [busy, setBusy] = useState(false);

  const loadStatus = useCallback(async (currentToken = token) => {
    if (!currentToken) {
      return;
    }
    const response = await fetch("/api/admin/ingestion/status", {
      headers: { Authorization: `Bearer ${currentToken}` }
    });
    if (!response.ok) {
      throw new Error("Unable to load ingestion status");
    }
    setStatus(await response.json());
  }, [token]);

  useEffect(() => {
    const stored = sessionStorage.getItem("apip_admin_token");
    if (stored) {
      setToken(stored);
      setMessage("Admin session restored");
      loadStatus(stored).catch(() => setMessage("Unable to load ingestion status"));
    }
  }, [loadStatus]);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
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
      await loadStatus(data.access_token);
    } finally {
      setBusy(false);
    }
  }

  async function runIngestion() {
    if (!token) {
      return;
    }
    setBusy(true);
    setMessage("Running live ingestion");
    try {
      const response = await fetch("/api/admin/ingestion/run", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail?.message ?? "Live ingestion failed");
        return;
      }
      setMessage(`Ingestion ${data.status}: ${data.records_created} records`);
      await loadStatus();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Live ingestion failed");
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <>
        <header className="grid gap-2 border-b border-border pb-6">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Admin</p>
          <h1 className="text-4xl font-semibold">Live Data Ingestion</h1>
        </header>
        <form className="grid max-w-md gap-3 rounded-md border border-border p-4" onSubmit={login}>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-4 w-4" />
            {message}
          </div>
          <input
            className="rounded-md border border-border bg-background px-3 py-2"
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            value={email}
          />
          <input
            className="rounded-md border border-border bg-background px-3 py-2"
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            type="password"
            value={password}
          />
          <Button disabled={busy} type="submit">
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Lock className="h-4 w-4" />}
            Sign in
          </Button>
        </form>
      </>
    );
  }

  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Admin</p>
        <h1 className="text-4xl font-semibold">Live Data Ingestion</h1>
        <p className="text-sm text-muted-foreground">{message}</p>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        <StatusCard label="Scheduler" value={status?.enabled ? "Enabled" : "Unknown"} />
        <StatusCard label="Interval" value={`${status?.interval_minutes ?? 30} minutes`} />
        <StatusCard label="Yahoo Finance" value={status?.yahoo_finance_enabled ? "Enabled" : "Disabled"} />
        <StatusCard label="SEC EDGAR" value={status?.sec_edgar_enabled ? "Enabled" : "Disabled"} />
      </section>

      <section className="grid gap-4 rounded-md border border-border p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">Manual Trigger</h2>
            <p className="text-sm text-muted-foreground">{status?.scheduler_task ?? "apip.ingest_live_data"}</p>
          </div>
          <Button disabled={busy} onClick={runIngestion}>
            {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            Run ingestion
          </Button>
        </div>
        {status?.last_run ? (
          <div className="grid gap-2 rounded-md bg-muted/30 p-3 text-sm">
            <span>Last run: {formatDate(status.last_run.started_at)}</span>
            <span>Completed: {formatDate(status.last_run.completed_at)}</span>
            <span>Records: {status.last_run.records_created}</span>
            <span>Failures: {status.last_run.records_failed}</span>
            <span>{status.last_run.message}</span>
          </div>
        ) : null}
      </section>

      <section className="grid gap-3">
        <h2 className="text-lg font-semibold">Recent Records</h2>
        {(status?.recent_records ?? []).map((record) => (
          <div className="grid gap-2 rounded-md border border-border p-3 text-sm" key={record.id}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <strong>
                {record.company_slug} / {record.metric_type}
              </strong>
              <Badge>{record.source_type}</Badge>
            </div>
            <div className="grid gap-1 text-xs text-muted-foreground md:grid-cols-4">
              <span>Confidence {record.confidence_score.toFixed(1)}</span>
              <span>Freshness {record.freshness_score}</span>
              <span>{record.ingestion_status}</span>
              <span>{formatDate(record.retrieved_at)}</span>
            </div>
          </div>
        ))}
      </section>
    </>
  );
}

function StatusCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-2 rounded-md border border-border p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <DatabaseZap className="h-4 w-4" />
        {label}
      </div>
      <strong>{value}</strong>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );
}
