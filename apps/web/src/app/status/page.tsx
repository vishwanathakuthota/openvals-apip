import type { Metadata } from "next";
import { Activity, CheckCircle2, Clock } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Status",
  description: "APIP public beta operational status and launch readiness.",
  alternates: { canonical: "/status" },
  openGraph: {
    title: "APIP Status",
    description: "Operational status for the OpenVals APIP public beta.",
    url: "/status",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP Status" }]
  }
};

const systems = [
  { name: "Public website", status: "Operational", note: "Landing, methodology, developer, and trust pages." },
  { name: "API", status: "Operational", note: "Health, catalog, metrics, confidence, and Trust Index routes." },
  { name: "Research workflow", status: "Beta", note: "Human review required before publish." },
  { name: "Billing", status: "Foundation", note: "Subscriptions and invoices are recorded; payments are future hooks." }
];

export default function StatusPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Operational Status</p>
        <h1 className="text-4xl font-semibold">APIP Status</h1>
      </header>
      <section className="grid gap-4 md:grid-cols-2">
        {systems.map((system) => (
          <Card key={system.name}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {system.status === "Operational" ? (
                  <CheckCircle2 className="h-5 w-5 text-primary" aria-hidden />
                ) : (
                  <Clock className="h-5 w-5 text-accent" aria-hidden />
                )}
                {system.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              <Badge className="w-fit">{system.status}</Badge>
              <p className="text-sm text-muted-foreground">{system.note}</p>
            </CardContent>
          </Card>
        ))}
      </section>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" aria-hidden />
            Status Policy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-6 text-muted-foreground">
            During public beta, OpenVals will publish material service interruptions, API availability issues, and
            trust-data publication incidents on this page and in release notes.
          </p>
        </CardContent>
      </Card>
    </>
  );
}
