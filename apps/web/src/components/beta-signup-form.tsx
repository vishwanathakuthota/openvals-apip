"use client";

import { FormEvent, useState } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";

type BetaSignupFormProps = {
  submissionType?: "waitlist" | "enterprise";
  compact?: boolean;
};

export function BetaSignupForm({ submissionType = "waitlist", compact = false }: BetaSignupFormProps) {
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");
    setMessage("");
    const form = new FormData(event.currentTarget);
    const payload = {
      submission_type: submissionType,
      name: String(form.get("name") ?? ""),
      email: String(form.get("email") ?? ""),
      organization: String(form.get("organization") ?? ""),
      role: String(form.get("role") ?? ""),
      interest: String(form.get("interest") ?? "")
    };
    try {
      const response = await fetch("/api/public-beta/signups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.message ?? data.message ?? "Submission failed");
      }
      event.currentTarget.reset();
      setStatus("success");
      setMessage(data.message ?? "Thanks. The OpenVals team received your request.");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Submission failed");
    }
  }

  return (
    <form className="grid gap-3" onSubmit={submit}>
      <div className={compact ? "grid gap-3 md:grid-cols-2" : "grid gap-3"}>
        <input
          className="h-11 rounded-md border border-border bg-background px-3 text-sm"
          name="name"
          placeholder="Name"
        />
        <input
          className="h-11 rounded-md border border-border bg-background px-3 text-sm"
          name="email"
          placeholder="Work email"
          required
          type="email"
        />
        <input
          className="h-11 rounded-md border border-border bg-background px-3 text-sm"
          name="organization"
          placeholder="Organization"
        />
        <input
          className="h-11 rounded-md border border-border bg-background px-3 text-sm"
          name="role"
          placeholder="Role"
        />
      </div>
      <textarea
        className="min-h-24 rounded-md border border-border bg-background px-3 py-2 text-sm"
        name="interest"
        placeholder={
          submissionType === "enterprise"
            ? "Tell us about your API, data, or enterprise validation needs"
            : "What would you like to evaluate during beta?"
        }
      />
      <Button disabled={status === "submitting"} type="submit">
        <Send className="h-4 w-4" aria-hidden />
        {status === "submitting"
          ? "Submitting"
          : submissionType === "enterprise"
            ? "Request Enterprise Access"
            : "Join Public Beta"}
      </Button>
      {message ? (
        <p className={status === "error" ? "text-sm text-destructive" : "text-sm text-primary"}>
          {message}
        </p>
      ) : null}
    </form>
  );
}
