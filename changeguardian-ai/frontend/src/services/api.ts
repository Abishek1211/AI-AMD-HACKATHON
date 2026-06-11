const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface AnalyzeChangeResponse {
  risk_score: number;
  confidence: number;
  recommendation: string;
  affected_services: string[];
  impact_level: string;
  explanation: string;
  incidents: Array<{
    id: string;
    title: string;
    severity: string;
    root_cause: string;
    impacted_services: string[];
  }>;
}

export async function analyzeChange(changeRequest: string): Promise<AnalyzeChangeResponse> {
  const res = await fetch(`${BASE_URL}/api/analyze-change`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ change_request: changeRequest }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function getRecentDecisions(limit = 10) {
  const res = await fetch(`${BASE_URL}/api/memory/recent?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch recent decisions");
  return res.json();
}
