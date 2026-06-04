import { adminProxyFetch } from "@/lib/api";

export async function GET() {
  return adminProxyFetch("source-metrics");
}
