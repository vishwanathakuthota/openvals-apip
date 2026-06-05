import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../../../proxy";

type RouteContext = {
  params: Promise<{ entityType: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const { entityType } = await context.params;
  return adminProxyFetch(`imports/catalog/${entityType}/csv`, {
    method: "POST",
    headers: authHeaders(request),
    body: await request.formData()
  });
}
