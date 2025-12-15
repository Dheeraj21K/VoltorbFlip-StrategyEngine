import type {
  AnalyzeRequest,
  AnalyzeResponse,
} from "../types";

// Standard Flask/FastAPI default port
const API_URL = "http://127.0.0.1:8000/analyze";

export async function analyzeBoard(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      let errorMessage = "Solver Error";
      
      try {
        const text = await res.text();
        
        // Try to parse as JSON first (FastAPI format)
        try {
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || text;
        } catch {
          // Plain text error
          errorMessage = text;
        }
        
        // Make errors more user-friendly and preserve formatting
        if (errorMessage.includes("⚠️")) {
          // Already formatted by backend
          throw new Error(errorMessage);
        }
        
        // Add context to common errors
        if (errorMessage.toLowerCase().includes("constraint")) {
          errorMessage = "❌ Invalid Board\n\n" + errorMessage;
        } else if (errorMessage.toLowerCase().includes("impossible")) {
          errorMessage = "❌ Impossible Configuration\n\n" + errorMessage;
        } else if (errorMessage.toLowerCase().includes("inconsistent")) {
          errorMessage = "❌ Inconsistent Constraints\n\n" + errorMessage;
        }
        
      } catch (parseError) {
        errorMessage = "Failed to parse error response from solver";
      }
      
      throw new Error(errorMessage);
    }

    const data = await res.json();

    // Normalize backend (snake_case) → frontend (camelCase)
    const normalizedRecommendations = (data.recommendations || []).map((r: any) => ({
      position: r.position,
      pVoltorb: r.p_voltorb ?? r.pVoltorb ?? 0,
      expectedValue: r.expected_value ?? r.expectedValue ?? 0,
      riskTier: r.risk_tier ?? r.riskTier ?? "UNKNOWN",
    }));

    return {
      guaranteed_safe: data.guaranteed_safe || [],
      guaranteed_voltorb: data.guaranteed_voltorb || [],
      recommendations: normalizedRecommendations,
      quit_recommended: data.quit_recommended || false,
      explanation: data.explanation || "Calculation complete.",
      mode: data.mode || "level",
    };
    
  } catch (error) {
    // Network errors or other fetch failures
    if (error instanceof Error) {
      throw error;
    }
    
    throw new Error(
      "Failed to connect to solver API. " +
      "Make sure the backend is running on http://127.0.0.1:8000"
    );
  }
}