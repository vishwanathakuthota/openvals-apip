"use client";

import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <Card>
      <CardContent className="grid min-h-80 place-items-center p-6 text-center">
        <div className="grid max-w-md gap-4">
          <AlertTriangle className="mx-auto h-9 w-9 text-destructive" aria-hidden />
          <div className="grid gap-2">
            <h1 className="text-2xl font-semibold">APIP could not load this view</h1>
            <p className="text-sm text-muted-foreground">
              The dashboard hit an unexpected data or rendering issue. Retry the request after the service recovers.
            </p>
          </div>
          <Button className="mx-auto" onClick={() => reset()}>
            Retry
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
