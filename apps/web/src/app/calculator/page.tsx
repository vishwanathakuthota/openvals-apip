import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CalculatorPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">AI Agent ROI</p>
        <h1 className="text-4xl font-semibold">Calculator</h1>
      </header>
      <Card>
        <CardHeader>
          <CardTitle>Inputs</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {["Users", "Tokens/User", "Provider", "Infrastructure Cost", "Employees", "Subscription Price"].map((label) => (
            <label className="grid gap-2 text-sm" key={label}>
              <span className="text-muted-foreground">{label}</span>
              <input className="h-10 rounded-md border border-border bg-background px-3 text-foreground" placeholder={label} />
            </label>
          ))}
        </CardContent>
      </Card>
    </>
  );
}
