const API_BASE_URL = process.env.WEB_PUBLIC_API_BASE_URL ?? process.env.APIP_API_BASE_URL;

export async function POST(request: Request) {
  if (!API_BASE_URL) {
    return Response.json(
      { code: "api_unavailable", message: "APIP_API_BASE_URL is not configured." },
      { status: 503 }
    );
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: await request.text(),
    cache: "no-store"
  });
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" }
  });
}
