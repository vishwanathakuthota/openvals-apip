import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../proxy";

type RouteContext = {
  params: Promise<{ resource: string; id: string }>;
};

export async function PATCH(request: Request, context: RouteContext) {
  const { resource, id } = await context.params;
  return adminProxyFetch(`${resource}/${id}`, {
    method: "PATCH",
    headers: {
      ...authHeaders(request),
      "Content-Type": "application/json"
    },
    body: await request.text()
  });
}

export async function POST(request: Request, context: RouteContext) {
  const { resource, id } = await context.params;
  return adminProxyFetch(`${resource}/${id}`, {
    method: "POST",
    headers: {
      ...authHeaders(request),
      "Content-Type": "application/json"
    },
    body: await request.text()
  });
}
