const API_BASE = "http://localhost:8000";

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/history`);

  if (!response.ok) {
    throw new Error(
      `History request failed: ${response.status}`
    );
  }

  const data = await response.json();

  return Array.isArray(data)
    ? data
    : data.results || [];
}