import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

import { createApp } from "../src/app.js";

async function main() {
  process.env.AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://127.0.0.1:8001";
  const pythonBin = process.env.PYTHON_BIN || "/home/xuelin/miniconda3/envs/rc-llm-eval/bin/python";

  const ai = spawn(pythonBin, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"], {
    cwd: "../ai_fastapi_postgresql/fastapi_service",
    stdio: "pipe",
  });

  ai.stderr.on("data", (chunk) => process.stderr.write(chunk));
  ai.stdout.on("data", (chunk) => process.stdout.write(chunk));
  await delay(1500);

  const app = createApp();
  const server = app.listen(0);
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}`;

  try {
    const health = await fetch(`${baseUrl}/health`);
    if (!health.ok) throw new Error(`health failed: ${health.status}`);

    const createdCourse = await fetch(`${baseUrl}/api/v1/admin/courses`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        title: "冒烟测试课程",
        description: "管理后台接口测试课程",
        levelCode: "beginner",
        sortOrder: 99,
        isPublished: true,
      }),
    });
    if (!createdCourse.ok) {
      throw new Error(`admin course create failed: ${createdCourse.status} ${await createdCourse.text()}`);
    }
    const courseId = (await createdCourse.json()).item.id;

    const createdLesson = await fetch(`${baseUrl}/api/v1/admin/lessons`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        courseId,
        title: "冒烟测试课时",
        description: "管理后台接口测试课时",
        sortOrder: 1,
      }),
    });
    if (!createdLesson.ok) {
      throw new Error(`admin lesson create failed: ${createdLesson.status} ${await createdLesson.text()}`);
    }

    const corpus = await fetch(`${baseUrl}/api/v1/corpus?type=sentence`).then((res) => res.json());
    if (!corpus.items?.length) throw new Error("sentence corpus is empty");

    const created = await fetch(`${baseUrl}/api/v1/admin/corpus`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        type: "word",
        hanzi: "早安",
        pinyin: "zǎo ān",
        translationEn: "good morning",
        difficulty: 1,
        tags: "word, greeting",
      }),
    });
    if (!created.ok) {
      throw new Error(`admin create failed: ${created.status} ${await created.text()}`);
    }
    const createdData = await created.json();
    const createdId = createdData.item.id;

    const updated = await fetch(`${baseUrl}/api/v1/admin/corpus/${createdId}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        type: "word",
        hanzi: "早上好",
        pinyin: "zǎo shang hǎo",
        translationEn: "good morning",
        difficulty: 1,
        tags: ["word", "greeting"],
      }),
    });
    if (!updated.ok) {
      throw new Error(`admin update failed: ${updated.status} ${await updated.text()}`);
    }

    const deleted = await fetch(`${baseUrl}/api/v1/admin/corpus/${createdId}`, { method: "DELETE" });
    if (deleted.status !== 204) {
      throw new Error(`admin delete failed: ${deleted.status} ${await deleted.text()}`);
    }

    const form = new FormData();
    form.append("corpusItemId", corpus.items[0].id);
    form.append("durationMs", "2800");
    form.append("audio", new Blob(["fake-audio"]), "practice.wav");

    const evaluated = await fetch(`${baseUrl}/api/v1/practice/evaluate`, {
      method: "POST",
      body: form,
    });
    if (!evaluated.ok) {
      throw new Error(`evaluate failed: ${evaluated.status} ${await evaluated.text()}`);
    }
    const result = await evaluated.json();
    if (!result.score?.overall_score) {
      throw new Error("missing pronunciation score");
    }
    const historyResponse = await fetch(`${baseUrl}/api/v1/practice/history`);
    if (!historyResponse.ok) {
      throw new Error(`practice history failed: ${historyResponse.status} ${await historyResponse.text()}`);
    }
    const history = await historyResponse.json();
    if (result.persistence?.persisted && !history.items?.some((item) => item.practiceRecordId === result.practiceRecordId)) {
      throw new Error("new practice record missing from history");
    }

    const practiceDetailResponse = await fetch(`${baseUrl}/api/v1/practice/${result.practiceRecordId}`);
    if (result.persistence?.persisted && !practiceDetailResponse.ok) {
      throw new Error(`practice detail failed: ${practiceDetailResponse.status} ${await practiceDetailResponse.text()}`);
    }
    if (result.persistence?.persisted) {
      const detailResponse = await fetch(`${baseUrl}/api/v1/admin/practice-scores/${result.practiceRecordId}`);
      if (!detailResponse.ok) {
        throw new Error(`score detail failed: ${detailResponse.status} ${await detailResponse.text()}`);
      }

      const annotationResponse = await fetch(`${baseUrl}/api/v1/admin/annotations`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          practiceRecordId: result.practiceRecordId,
          errorType: "tone",
          note: "三声需要更完整",
          startMs: 0,
          endMs: 900,
        }),
      });
      if (!annotationResponse.ok) {
        throw new Error(`annotation create failed: ${annotationResponse.status} ${await annotationResponse.text()}`);
      }
    }
    console.log("Node smoke test passed:", result.score.overall_score);
  } finally {
    server.close();
    ai.kill("SIGTERM");
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
