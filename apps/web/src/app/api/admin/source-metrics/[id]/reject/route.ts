import { adminProxyFetch } from "@/lib/api";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function PATCH(_: Request, context: RouteContext) {
  const { id } = await context.params;
  return adminProxyFetch(`source-metrics/${id}/reject`, { method: "PATCH" });
}
