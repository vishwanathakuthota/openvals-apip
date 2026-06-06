import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "@/app/api/admin/proxy";

type RouteContext = { params: Promise<{ agentName: string }> };

export async function POST(request: Request, context: RouteContext) {
  const { agentName } = await context.params;
  return adminProxyFetch(`autonomous-research/run/${agentName}`, {
    method: "POST",
    headers: authHeaders(request)
  });
}
