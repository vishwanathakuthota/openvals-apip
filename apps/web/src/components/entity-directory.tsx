import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Entity } from "@/types/api";

export function EntityDirectory({ basePath, items }: { basePath: string; items: Entity[] }) {
  return (
    <div className="grid gap-3">
      {items.map((item) => (
        <Link href={`${basePath}/${item.id}`} key={item.id}>
          <Card className="transition-colors hover:border-primary/60 hover:bg-muted/40">
            <CardContent className="flex items-center justify-between gap-4 p-4">
              <div className="grid gap-1">
                <strong>{item.name}</strong>
                <span className="text-sm text-muted-foreground">{item.slug ?? item.id}</span>
              </div>
              <div className="flex items-center gap-3">
                {item.ticker ? <Badge>{item.ticker}</Badge> : null}
                {item.iso_code ? <Badge>{item.iso_code}</Badge> : null}
                {item.model_family ? <Badge>{item.model_family}</Badge> : null}
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
