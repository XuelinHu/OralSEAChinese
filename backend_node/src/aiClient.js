import { config } from "./config.js";

export async function evaluatePronunciation(payload) {
  const response = await fetch(`${config.aiServiceUrl}/api/v1/pronunciation/evaluate`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`AI service failed: ${response.status} ${text}`);
  }

  return response.json();
}
