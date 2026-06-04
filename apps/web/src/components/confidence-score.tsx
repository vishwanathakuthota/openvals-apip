import { ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { Confidence } from "@/types/api";

const dimensions = [
  ["Source Reliability", "source_reliability"],
  ["Data Freshness", "data_freshness"],
  ["Cross Verification", "cross_verification"],
  ["Methodology Transparency", "methodology_transparency"]
] as const;

export function ConfidenceScore({ confidence }: { confidence: Confidence | null }) {
  if (!confidence) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            Confidence Score Engine
          </CardTitle>
          <p className="text-sm text-muted-foreground">Evidence quality, freshness, verification, and transparency.</p>
        </div>
        <Badge>{confidence.label}</Badge>
      </CardHeader>
      <CardContent className="grid gap-5">
        <div className="grid gap-2">
          <div className="flex items-end justify-between">
            <strong className="text-4xl">{confidence.score.toFixed(1)}</strong>
            <span className="text-sm text-muted-foreground">{confidence.source_count} sources</span>
          </div>
          <Progress value={confidence.score} />
        </div>
        <div className="grid gap-3">
          {dimensions.map(([label, key]) => (
            <div className="grid gap-1" key={key}>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{label}</span>
                <span>{confidence[key] ?? "n/a"}</span>
              </div>
              <Progress value={Number(confidence[key] ?? 0)} className="h-1.5" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
