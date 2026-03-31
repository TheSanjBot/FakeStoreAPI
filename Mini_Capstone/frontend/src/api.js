const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

function getErrorMessage(payload) {
  if (!payload) {
    return "Something went wrong.";
  }

  if (typeof payload === "string") {
    return payload;
  }

  if (Array.isArray(payload.detail)) {
    return payload.detail.map((item) => item.msg || item.detail || "Invalid request.").join(", ");
  }

  if (payload.detail) {
    return payload.detail;
  }

  return "Something went wrong.";
}

export async function apiRequest(path, options = {}) {
  const { method = "GET", body, token } = options;
  const headers = {
    Accept: "application/json"
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined
  });

  const text = await response.text();
  let payload = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    throw new Error(getErrorMessage(payload));
  }

  return payload;
}

export { API_BASE_URL };
