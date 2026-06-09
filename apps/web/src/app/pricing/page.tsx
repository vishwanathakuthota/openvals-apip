import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Pricing",
  description: "APIP public beta API plans for Community, Research, Professional, and Enterprise access.",
  alternates: { canonical: "/pricing" },
  openGraph: {
    title: "APIP Pricing",
    description: "API access plans for source-backed AI profitability intelligence.",
    url: "/pricing",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP Pricing" }]
  }
};

const plans = [
  { name: "Community", price: "$0", quota: "100/day", badge: "Beta starter" },
  { name: "Research", price: "$99/mo", quota: "1,000/day", badge: "Research teams" },
  { name: "Professional", price: "$499/mo", quota: "5,000/day", badge: "Commercial API" },
  { name: "Enterprise", price: "Contract", quota: "Unlimited", badge: "Custom SLA" }
];

export default function PricingPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">API Plans</p>
        <h1 className="text-4xl font-semibold">Public Beta Pricing</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Plans define daily API quota and entitlement posture. Commercial billing records are in place for public beta;
          payment processor integration is planned for a later launch stage.
        </p>
      </header>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {plans.map((plan) => (
          <Card key={plan.name}>
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              <strong className="text-2xl">{plan.price}</strong>
              <span className="text-sm text-muted-foreground">{plan.quota}</span>
              <Badge>{plan.badge}</Badge>
            </CardContent>
          </Card>
        ))}
      </section>
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-3 p-5">
          <p className="text-sm text-muted-foreground">Need custom validation workflows, usage limits, or support?</p>
          <Link className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground" href="/contact">
            Contact OpenVals
          </Link>
        </CardContent>
      </Card>
    </>
  );
}
