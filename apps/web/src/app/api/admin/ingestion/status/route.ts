import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../proxy";

export async function GET(request: Request) {
  return adminProxyFetch("ingestion/status", { headers: authHeaders(request) });
}
