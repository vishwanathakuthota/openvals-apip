import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../proxy";

type RouteContext = {
  params: Promise<{ resource: string }>;
};

export async function GET(request: Request, context: RouteContext) {
  const { resource } = await context.params;
  return adminProxyFetch(resource, { headers: authHeaders(request) });
}

export async function POST(request: Request, context: RouteContext) {
  const { resource } = await context.params;
  return adminProxyFetch(resource, {
    method: "POST",
    headers: {
      ...authHeaders(request),
      "Content-Type": "application/json"
    },
    body: await request.text()
  });
}
