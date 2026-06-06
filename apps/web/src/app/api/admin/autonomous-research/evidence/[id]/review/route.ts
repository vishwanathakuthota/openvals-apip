import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "@/app/api/admin/proxy";

type RouteContext = { params: Promise<{ id: string }> };

export async function PATCH(request: Request, context: RouteContext) {
  const { id } = await context.params;
  const body = await request.text();
  return adminProxyFetch(`autonomous-research/evidence/${id}/review`, {
    method: "PATCH",
    headers: authHeaders(request),
    body
  });
}
