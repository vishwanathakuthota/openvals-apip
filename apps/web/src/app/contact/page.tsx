import type { Metadata } from "next";

import { BetaSignupForm } from "@/components/beta-signup-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Contact",
  description: "Contact OpenVals for APIP public beta access, enterprise API plans, and validation partnerships.",
  alternates: { canonical: "/contact" },
  openGraph: {
    title: "Contact OpenVals APIP",
    description: "Enterprise APIP inquiries, API access, and validation partnerships.",
    url: "/contact",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "Contact OpenVals APIP" }]
  }
};

export default function ContactPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Contact</p>
        <h1 className="text-4xl font-semibold">Enterprise Inquiry</h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Use this form for API access, research partnerships, enterprise validation programs, and source-backed AI
          economics workflows.
        </p>
      </header>
      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Best For</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm text-muted-foreground">
            <p>Institutional research teams validating AI economics.</p>
            <p>Enterprise teams that need higher API volumes or custom SLAs.</p>
            <p>Partners with source-backed datasets or validation workflows.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Request Access</CardTitle>
          </CardHeader>
          <CardContent>
            <BetaSignupForm submissionType="enterprise" />
          </CardContent>
        </Card>
      </section>
    </>
  );
}
