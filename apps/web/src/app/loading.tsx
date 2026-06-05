import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function Loading() {
  return (
    <div className="grid gap-6" aria-label="Loading APIP data">
      <div className="grid gap-3 border-b border-border pb-6">
        <div className="h-3 w-48 animate-pulse rounded bg-muted" />
        <div className="h-10 w-full max-w-xl animate-pulse rounded bg-muted" />
        <div className="h-4 w-full max-w-2xl animate-pulse rounded bg-muted" />
      </div>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="h-4 w-28 animate-pulse rounded bg-muted" />
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="h-8 w-32 animate-pulse rounded bg-muted" />
              <div className="h-3 w-full animate-pulse rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </section>
      <Card>
        <CardContent className="h-80 animate-pulse rounded bg-muted/60" />
      </Card>
    </div>
  );
}
