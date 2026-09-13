const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: options.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // ignore -- body wasn't JSON
    }
    throw new Error(detail);
  }
  return res.json();
}

export function lookupProduct(query, queryType = "auto") {
  return request("/api/product/lookup", {
    method: "POST",
    body: JSON.stringify({ query, query_type: queryType }),
  });
}

export function lookupCandidate(url) {
  return request("/api/product/lookup/candidate", {
    method: "POST",
    body: JSON.stringify({ query: url, query_type: "url" }),
  });
}

export function createSession() {
  return request("/api/excel/new", { method: "POST" });
}

export async function uploadExcel(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/excel/upload", { method: "POST", body: formData });
}

export function getRows(sessionId) {
  return request(`/api/excel/${sessionId}/rows`);
}

export function updateExcel(sessionId, product) {
  return request("/api/excel/update", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, product }),
  });
}

export function downloadUrl(sessionId) {
  return `${API_BASE}/api/excel/${sessionId}/download`;
}
