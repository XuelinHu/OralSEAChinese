import { config } from "./config.js";
import fs from "node:fs/promises";

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

export async function evaluatePronunciationAudio(payload, audioFilePath) {
  if (!audioFilePath) {
    return evaluatePronunciation(payload);
  }

  const form = new FormData();
  form.append("corpus_type", payload.corpus_type);
  form.append("hanzi", payload.hanzi);
  form.append("pinyin", payload.pinyin);
  const audioContent = await fs.readFile(audioFilePath);
  form.append("audio", new Blob([audioContent], { type: "audio/wav" }), "practice.wav");

  const response = await fetch(`${config.aiServiceUrl}/api/v1/pronunciation/evaluate-audio`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`AI audio service failed: ${response.status} ${text}`);
  }

  return response.json();
}
