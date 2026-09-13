import { mockScans } from "../mock/scans";

// Set VITE_API_BASE_URL in a .env file (see .env.example) once you know
// where the backend is running — defaults to localhost:8000, FastAPI's
// usual default port.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Fetches scan history from the real backend (GET /history).
 * Falls back to mock data if the backend isn't reachable, so the frontend
 * keeps working during standalone development or if the backend crashes
 * mid-demo. `source` on the return value tells you which one you got.
 */
export async function fetchHistory() {
  try {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error(`GET /history failed: ${res.status}`);
    const data = await res.json();
    // Backend might return a bare array, or a wrapped { results: [...] } —
    // handle both until the exact response shape is confirmed.
    const scans = Array.isArray(data) ? data : (data.results ?? []);
    return { scans, source: "live" };
  } catch (err) {
    console.warn("Falling back to mock data — backend not reachable:", err.message);
    return { scans: mockScans, source: "mock" };
  }
}

/**
 * Uploads an image to POST /scan and returns the resulting scan object.
 * Not used on your pages yet (that's Person 4's Scan screen) but here so
 * it's ready when you need it — e.g. for a "re-scan" action from History.
 */
export async function postScan(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/scan`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`POST /scan failed: ${res.status}`);
  return res.json();
}
