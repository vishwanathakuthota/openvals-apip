export function authHeaders(request: Request) {
  return { Authorization: request.headers.get("Authorization") ?? "" };
}
