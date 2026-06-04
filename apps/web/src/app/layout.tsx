import type { Metadata } from "next";
import Link from "next/link";
import { BarChart3, Building2, Calculator, Globe2, Landmark, Orbit, ShieldCheck } from "lucide-react";

import "../styles/globals.css";

export const metadata: Metadata = {
  title: "APIP",
  description: "AI Profitability Intelligence Platform"
};

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/industries", label: "Industries", icon: Landmark },
  { href: "/countries", label: "Countries", icon: Globe2 },
  { href: "/models", label: "Models", icon: ShieldCheck },
  { href: "/reality-index", label: "AI Reality Index", icon: Orbit },
  { href: "/calculator", label: "ROI Calculator", icon: Calculator }
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html className="dark" lang="en">
      <body>
        <div className="min-h-screen bg-background text-foreground">
          <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-border bg-card/80 p-5 backdrop-blur lg:block">
            <Link className="mb-8 flex items-center gap-3" href="/">
              <span className="grid h-11 w-11 place-items-center rounded-md bg-primary font-black text-primary-foreground">
                AP
              </span>
              <span className="grid">
                <strong>APIP</strong>
                <small className="text-muted-foreground">Profitability Intelligence</small>
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
          </aside>
          <div className="border-b border-border bg-card/80 p-4 lg:hidden">
            <strong>APIP</strong>
          </div>
          <main className="lg:pl-72">
            <div className="mx-auto grid max-w-7xl gap-6 p-5 lg:p-8">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
