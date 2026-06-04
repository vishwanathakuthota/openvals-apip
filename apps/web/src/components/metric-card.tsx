import { formatMetric } from "@/lib/format";

import { Card, CardContent } from "./ui/card";

export function MetricCard({ label, value, unit }: { label: string; value: number; unit: string }) {
  return (
    <Card>
      <CardContent className="grid gap-3 p-5">
        <span className="text-sm text-muted-foreground">{label}</span>
        <strong className="text-2xl">{formatMetric(value, unit)}</strong>
      </CardContent>
    </Card>
  );
}
