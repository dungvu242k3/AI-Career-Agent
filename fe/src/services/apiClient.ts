import { getAccessToken, refreshAccessToken } from "./authApi";

/**
 * Fetch wrapper for the FastAPI resource server.
 *
 * Keeping the authorization concern in one place prevents a newly added API
 * client from accidentally becoming an unauthenticated path.
 */
export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const send = async (token: string | null): Promise<Response> => {
    const headers = new Headers(init.headers);
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    return fetch(input, { ...init, headers, credentials: "include" });
  };

  const response = await send(getAccessToken());
  if (response.status !== 401) return response;

  const token = await refreshAccessToken();
  if (token) {
    return send(token);
  }
  return response;
}
