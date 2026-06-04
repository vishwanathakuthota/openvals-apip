import { adminProxyFetch } from "@/lib/api";

export async function POST(request: Request) {
  return adminProxyFetch("imports/csv", {
    method: "POST",
    body: await request.formData()
  });
}
