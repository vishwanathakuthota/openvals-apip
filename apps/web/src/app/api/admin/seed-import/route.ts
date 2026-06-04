import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../proxy";

export async function POST(request: Request) {
  return adminProxyFetch("seed-import", {
    method: "POST",
    headers: authHeaders(request)
  });
}
