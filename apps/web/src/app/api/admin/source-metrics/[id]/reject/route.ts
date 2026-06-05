import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../../proxy";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function PATCH(request: Request, context: RouteContext) {
  const { id } = await context.params;
  return adminProxyFetch(`source-metrics/${id}/reject`, {
    method: "PATCH",
    headers: authHeaders(request)
  });
}
