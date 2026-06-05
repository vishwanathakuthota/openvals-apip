import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="grid gap-4">
      <EmptyState
        title="Page not found"
        message="This APIP route is not available in the Version 1 launch surface."
      />
      <Button asChild className="w-fit">
        <Link href="/">Return to dashboard</Link>
      </Button>
    </div>
  );
}
