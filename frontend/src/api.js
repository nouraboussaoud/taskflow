const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api/v1";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function api(path, { token, method = "GET", body, signal } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    signal,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) return null;

  let payload;
  try {
    payload = await response.json();
  } catch {
    if (response.ok) throw new ApiError("The server returned an invalid response.", response.status);
    payload = null;
  }
  if (!response.ok) {
    throw new ApiError(payload?.error?.message || "The request could not be completed.", response.status);
  }
  return payload;
}
