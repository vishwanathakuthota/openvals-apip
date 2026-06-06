import type { Metadata } from "next";
import Link from "next/link";
import {
  BarChart3,
  BookOpen,
  Building2,
  Calculator,
  Code2,
  FileWarning,
  Globe2,
  Info,
  Landmark,
  Orbit,
  ShieldCheck
} from "lucide-react";

import "../styles/globals.css";

const siteUrl = "https://apip.openvalidations.com";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "APIP by OpenVals",
    template: "%s | APIP"
  },
  description:
    "APIP by OpenVals measures whether AI investments are producing real economic value with transparent metrics, sources, confidence scores, and AI Reality Index rankings.",
  alternates: {
    canonical: "/"
  },
  openGraph: {
    title: "APIP by OpenVals",
    description:
      "Evidence-based AI profitability intelligence for companies, industries, countries, and model economics.",
    url: siteUrl,
    siteName: "APIP",
    images: [{ url: "/og-image.svg", width: 1200, height: 630, alt: "APIP by OpenVals" }],
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "APIP by OpenVals",
    description: "AI profitability intelligence with transparent evidence and confidence scores.",
    images: ["/og-image.svg"]
  },
  icons: {
    icon: "/favicon.svg"
  }
};

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/industries", label: "Industries", icon: Landmark },
  { href: "/countries", label: "Countries", icon: Globe2 },
  { href: "/models", label: "Models", icon: ShieldCheck },
  { href: "/reality-index", label: "AI Reality Index", icon: Orbit },
  { href: "/trust-center", label: "Trust Center", icon: ShieldCheck },
  { href: "/calculator", label: "ROI Calculator", icon: Calculator },
  { href: "/developers", label: "Developers", icon: Code2 }
];

const footerLinks = [
  { href: "/methodology", label: "Methodology", icon: BookOpen },
  { href: "/trust-center", label: "Trust Center", icon: ShieldCheck },
  { href: "/about", label: "About", icon: Info },
  { href: "/disclaimer", label: "Disclaimer", icon: FileWarning },
  { href: "/developers", label: "Developers", icon: Code2 }
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html className="dark" lang="en">
      <body>
        <div className="min-h-screen bg-background text-foreground">
          <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-border bg-card/80 p-5 backdrop-blur lg:block">
            <Link className="mb-8 flex items-center gap-3" href="/">
              <span className="grid h-11 w-11 place-items-center rounded-md bg-primary font-black text-primary-foreground">
                OV
              </span>
              <span className="grid">
                <strong>OpenVals APIP</strong>
                <small className="text-muted-foreground">AI Profitability Intelligence</small>
              </span>
            </Link>
            <nav className="grid gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    href={item.href}
                    key={item.href}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            <div className="absolute bottom-5 left-5 right-5 grid gap-2 border-t border-border pt-4 text-xs text-muted-foreground">
              <span>OpenVals V1 launch preview</span>
              <span>apip.openvalidations.com</span>
            </div>
          </aside>
          <div className="border-b border-border bg-card/80 p-4 lg:hidden">
            <div className="flex items-center justify-between gap-3">
              <Link className="flex items-center gap-2" href="/">
                <span className="grid h-9 w-9 place-items-center rounded-md bg-primary font-black text-primary-foreground">
                  OV
                </span>
                <strong>APIP</strong>
              </Link>
              <Link className="text-sm text-primary" href="/developers">
                API Docs
              </Link>
            </div>
            <nav className="mt-3 flex gap-2 overflow-x-auto pb-1">
              {navItems.map((item) => (
                <Link
                  className="shrink-0 rounded-md border border-border px-3 py-2 text-xs text-muted-foreground"
                  href={item.href}
                  key={item.href}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <main className="lg:pl-72">
            <div className="mx-auto grid max-w-7xl gap-6 p-5 lg:p-8">
              {children}
              <footer className="mt-6 grid gap-4 border-t border-border pt-6 text-sm text-muted-foreground md:flex md:items-center md:justify-between">
                <div className="grid gap-1">
                  <strong className="text-foreground">OpenVals APIP</strong>
                  <span>Evidence-based AI profitability intelligence for V1 launch.</span>
                </div>
                <nav className="flex flex-wrap gap-3">
                  {footerLinks.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        className="inline-flex items-center gap-1 hover:text-foreground"
                        href={item.href}
                        key={item.href}
                      >
                        <Icon className="h-4 w-4" />
                        {item.label}
                      </Link>
                    );
                  })}
                </nav>
              </footer>
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
