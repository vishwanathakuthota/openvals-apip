import { adminProxyFetch } from "@/lib/api";
import { authHeaders } from "../../proxy";

export async function POST(request: Request) {
  return adminProxyFetch("imports/csv", {
    method: "POST",
    headers: authHeaders(request),
    body: await request.formData()
  });
}
