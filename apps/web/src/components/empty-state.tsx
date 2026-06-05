import { SearchX } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <Card>
      <CardContent className="grid min-h-48 place-items-center p-6 text-center">
        <div className="grid max-w-md gap-3">
          <SearchX className="mx-auto h-8 w-8 text-muted-foreground" aria-hidden />
          <strong className="text-lg">{title}</strong>
          <p className="text-sm text-muted-foreground">{message}</p>
        </div>
      </CardContent>
    </Card>
  );
}
