import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const examples = [
  {
    title: "Companies",
    command: "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/companies"
  },
  {
    title: "Industries",
    command: "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/industries"
  },
  {
    title: "Metrics",
    command:
      "curl -H 'X-API-Key: apip_live_...' 'https://apip.openvalidations.com/api/v1/metrics/search?entity_type=company&metric_key=ai_revenue'"
  },
  {
    title: "Confidence",
    command:
      "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/confidence/{metric_value_id}"
  },
  {
    title: "AI Reality Index",
    command: "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/ai-reality-index"
  },
  {
    title: "Trust Index",
    command: "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/trust-index"
  },
  {
    title: "Source Lineage",
    command: "curl -H 'X-API-Key: apip_live_...' https://apip.openvalidations.com/api/v1/source-lineage"
  }
];

const plans = [
  {
    name: "Community",
    quota: "100/day",
    price: "$0",
    badge: "Starter",
    description: "Public API access for pilots and local integrations."
  },
  {
    name: "Research",
    quota: "1,000/day",
    price: "$99/mo",
    badge: "Research",
    description: "Higher request volume with source lineage and export-ready evidence."
  },
  {
    name: "Professional",
    quota: "5,000/day",
    price: "$499/mo",
    badge: "Commercial",
    description: "Production API access with Trust Index history and priority support."
  },
  {
    name: "Enterprise",
    quota: "Unlimited",
    price: "Contract",
    badge: "SLA",
    description: "Custom quotas, contract terms, and enterprise support hooks."
  }
];

export default function DevelopersPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Public API</p>
        <h1 className="text-4xl font-semibold">Developer Access</h1>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {plans.map((plan) => (
          <Card key={plan.name}>
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              <strong className="text-2xl">{plan.quota}</strong>
              <span className="text-sm text-muted-foreground">{plan.price}</span>
              <Badge>{plan.badge}</Badge>
              <p className="text-sm text-muted-foreground">{plan.description}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Authentication</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <pre className="overflow-x-auto rounded-md border border-border bg-background p-4 text-sm">
              <code>X-API-Key: apip_live_...</code>
            </pre>
            <p className="text-sm text-muted-foreground">
              Admins can create, rotate, and revoke keys from the APIP admin portal. Each request is
              metered by key, endpoint, method, and plan.
            </p>
          </CardContent>
        </Card>

        {examples.map((example) => (
          <Card key={example.title}>
            <CardHeader>
              <CardTitle>{example.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="overflow-x-auto rounded-md border border-border bg-background p-4 text-sm">
                <code>{example.command}</code>
              </pre>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
