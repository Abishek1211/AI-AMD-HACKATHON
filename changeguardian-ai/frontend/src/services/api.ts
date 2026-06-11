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

