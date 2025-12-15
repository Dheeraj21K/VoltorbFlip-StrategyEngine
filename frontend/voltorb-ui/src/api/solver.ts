import type {
  AnalyzeRequest,
  AnalyzeResponse,
} from "../types";

// Standard Flask/FastAPI default port
const API_URL = "http://127.0.0.1:8000/analyze";

export async function analyzeBoard(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Solver Error: ${text}`);
  }

  const data = await res.json();

  // 🔹 NORMALIZE backend (snake_case) → frontend (camelCase)
  // We explicitly map the fields here to prevent UI crashes if backend naming varies
  const normalizedRecommendations = data.recommendations.map((r: any) => ({
    position: r.position,
    pVoltorb: r.p_voltorb ?? r.voltorb_risk, // Handle both naming conventions just in case
    expectedValue: r.expected_value,
    riskTier: r.risk_tier,
  }));

  return {
    guaranteed_safe: data.guaranteed_safe || [],
    guaranteed_voltorb: data.guaranteed_voltorb || [],
    recommendations: normalizedRecommendations,
    quit_recommended: data.quit_recommended || false,
    explanation: data.explanation || "Calculation complete.",
    mode: data.mode || "level",
  };
}