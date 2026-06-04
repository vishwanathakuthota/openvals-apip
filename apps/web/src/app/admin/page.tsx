import { AdminPortal } from "@/components/admin/admin-portal";

export default function AdminPage() {
  return (
    <>
      <header className="grid gap-2 border-b border-border pb-6">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Operations</p>
        <h1 className="text-4xl font-semibold">Admin Portal</h1>
      </header>
      <AdminPortal />
    </>
  );
}
