import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../../proxy";

type RouteContext = {
  params: Promise<{ resource: string; id: string; action: string }>;
};

export async function PATCH(request: Request, context: RouteContext) {
  const { resource, id, action } = await context.params;
  return adminProxyFetch(`${resource}/${id}/${action}`, {
    method: "PATCH",
    headers: authHeaders(request)
  });
}
