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
  }
];

export default function DevelopersPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Public API</p>
        <h1 className="text-4xl font-semibold">Developer Access</h1>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Free</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <strong className="text-2xl">100/day</strong>
            <Badge>Default</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Pro</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <strong className="text-2xl">5,000/day</strong>
            <Badge>Partner</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Enterprise</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <strong className="text-2xl">Unlimited</strong>
            <Badge>Contract</Badge>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Authentication</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded-md border border-border bg-background p-4 text-sm">
              <code>X-API-Key: apip_live_...</code>
            </pre>
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
