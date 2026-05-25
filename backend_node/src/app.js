import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import cors from "cors";
import express from "express";
import multer from "multer";

import { evaluatePronunciation } from "./aiClient.js";
import {
  healthCheckDatabase,
  createCourse,
  createAnnotation,
  createCorpusItem,
  createLesson,
  deleteCorpusItem,
  deleteAnnotation,
  getPracticeScore,
  getCorpusItem,
  listCorpusItems,
  listCourses,
  listAnnotations,
  listLessons,
  listPracticeScores,
  savePracticeEvaluation,
  updateCourse,
  updateAnnotation,
  updateCorpusItem,
  updateLesson,
} from "./repository.js";
import { config } from "./config.js";

const uploadRoot = path.resolve(process.cwd(), config.uploadDir);
fs.mkdirSync(uploadRoot, { recursive: true });
const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, callback) => callback(null, uploadRoot),
    filename: (_req, file, callback) => {
      const safeName = file.originalname.replace(/[^\w.-]/g, "_");
      callback(null, `${Date.now()}-${crypto.randomUUID()}-${safeName}`);
    },
  }),
});

export function createApp() {
  const app = express();
  app.use(cors());
  app.use(express.json({ limit: "2mb" }));
  app.use("/uploads", express.static(uploadRoot));

  app.get("/health", async (_req, res, next) => {
    try {
      let database;
      try {
        database = await healthCheckDatabase();
      } catch (error) {
        database = { connected: false, mode: "postgresql", error: error.message };
      }
      res.json({ status: "ok", service: "backend-node", database });
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/auth/login", (req, res) => {
    const { username } = req.body;
    res.json({
      token: "dev-token",
      user: {
        id: "00000000-0000-0000-0000-000000000001",
        username: username || "learner",
        displayName: "Demo Learner",
        role: "learner",
      },
    });
  });

  app.get("/api/v1/courses", async (_req, res, next) => {
    try {
      res.json({ items: await listCourses() });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/courses/:courseId/lessons", async (req, res, next) => {
    try {
      res.json({ items: await listLessons(req.params.courseId) });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/corpus", async (req, res, next) => {
    try {
      res.json({
        items: await listCorpusItems({
          type: req.query.type,
          lessonId: req.query.lessonId,
        }),
      });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/corpus", async (req, res, next) => {
    try {
      res.json({
        items: await listCorpusItems({
          type: req.query.type,
          lessonId: req.query.lessonId,
        }),
      });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/courses", async (_req, res, next) => {
    try {
      res.json({ items: await listCourses() });
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/admin/courses", async (req, res, next) => {
    try {
      const validationError = validateCoursePayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      res.status(201).json({ item: await createCourse(req.body) });
    } catch (error) {
      next(error);
    }
  });

  app.put("/api/v1/admin/courses/:id", async (req, res, next) => {
    try {
      const validationError = validateCoursePayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      const item = await updateCourse(req.params.id, req.body);
      if (!item) {
        res.status(404).json({ error: "Course not found" });
        return;
      }
      res.json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/courses/:courseId/lessons", async (req, res, next) => {
    try {
      res.json({ items: await listLessons(req.params.courseId) });
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/admin/lessons", async (req, res, next) => {
    try {
      const validationError = validateLessonPayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      res.status(201).json({ item: await createLesson(req.body) });
    } catch (error) {
      next(error);
    }
  });

  app.put("/api/v1/admin/lessons/:id", async (req, res, next) => {
    try {
      const validationError = validateLessonPayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      const item = await updateLesson(req.params.id, req.body);
      if (!item) {
        res.status(404).json({ error: "Lesson not found" });
        return;
      }
      res.json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/admin/corpus", async (req, res, next) => {
    try {
      const validationError = validateCorpusPayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }

      const item = await createCorpusItem(req.body);
      res.status(201).json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.put("/api/v1/admin/corpus/:id", async (req, res, next) => {
    try {
      const validationError = validateCorpusPayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }

      const item = await updateCorpusItem(req.params.id, req.body);
      if (!item) {
        res.status(404).json({ error: "Corpus item not found" });
        return;
      }
      res.json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.delete("/api/v1/admin/corpus/:id", async (req, res, next) => {
    try {
      const deleted = await deleteCorpusItem(req.params.id);
      if (!deleted) {
        res.status(404).json({ error: "Corpus item not found" });
        return;
      }
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/practice-scores", async (req, res, next) => {
    try {
      const limit = Math.min(Number(req.query.limit || 50), 200);
      res.json({ items: await listPracticeScores(limit) });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/practice-scores/:id", async (req, res, next) => {
    try {
      const item = await getPracticeScore(req.params.id);
      if (!item) {
        res.status(404).json({ error: "Practice score not found" });
        return;
      }
      res.json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/v1/admin/annotations", async (req, res, next) => {
    try {
      res.json({
        items: await listAnnotations({
          practiceRecordId: req.query.practiceRecordId,
        }),
      });
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/admin/annotations", async (req, res, next) => {
    try {
      const validationError = validateAnnotationPayload(req.body);
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      res.status(201).json({ item: await createAnnotation(req.body) });
    } catch (error) {
      next(error);
    }
  });

  app.put("/api/v1/admin/annotations/:id", async (req, res, next) => {
    try {
      const validationError = validateAnnotationPayload(req.body, { requirePracticeRecordId: false });
      if (validationError) {
        res.status(400).json({ error: validationError });
        return;
      }
      const item = await updateAnnotation(req.params.id, req.body);
      if (!item) {
        res.status(404).json({ error: "Annotation not found" });
        return;
      }
      res.json({ item });
    } catch (error) {
      next(error);
    }
  });

  app.delete("/api/v1/admin/annotations/:id", async (req, res, next) => {
    try {
      const deleted = await deleteAnnotation(req.params.id);
      if (!deleted) {
        res.status(404).json({ error: "Annotation not found" });
        return;
      }
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/v1/practice/evaluate", upload.single("audio"), async (req, res, next) => {
    try {
      const corpusItem = await getCorpusItem(req.body.corpusItemId);
      if (!corpusItem) {
        res.status(404).json({ error: "Corpus item not found" });
        return;
      }

      const practiceRecordId = crypto.randomUUID();
      const audioSize = req.file?.size || 0;
      const result = await evaluatePronunciation({
        practice_record_id: practiceRecordId,
        corpus_item_id: corpusItem.id,
        corpus_type: corpusItem.type,
        hanzi: corpusItem.hanzi,
        pinyin: corpusItem.pinyin,
        audio_url: audioSize > 0 ? `/uploads/${req.file.filename}` : null,
        duration_ms: Number(req.body.durationMs || 0) || null,
      });
      const audio = {
        received: audioSize > 0,
        size: audioSize,
        filename: req.file?.originalname || null,
        storagePath: audioSize > 0 ? `/uploads/${req.file.filename}` : null,
        mimeType: req.file?.mimetype || "audio/wav",
        durationMs: Number(req.body.durationMs || 0) || null,
      };
      const persistence = await savePracticeEvaluation({
        practiceRecordId,
        corpusItemId: corpusItem.id,
        audio,
        score: result,
      });

      res.json({
        practiceRecordId,
        corpusItem,
        audio,
        score: result,
        persistence,
      });
    } catch (error) {
      next(error);
    }
  });

  app.use((error, _req, res, _next) => {
    res.status(500).json({ error: error.message || "Internal server error" });
  });

  return app;
}

function validateCoursePayload(payload) {
  if (!payload.title || typeof payload.title !== "string") {
    return "title is required";
  }
  return null;
}

function validateLessonPayload(payload) {
  if (!payload.courseId || typeof payload.courseId !== "string") {
    return "courseId is required";
  }
  if (!payload.title || typeof payload.title !== "string") {
    return "title is required";
  }
  return null;
}

function validateCorpusPayload(payload) {
  const allowedTypes = new Set(["pinyin", "word", "sentence"]);
  if (!allowedTypes.has(payload.type)) {
    return "type must be one of pinyin, word, sentence";
  }
  if (!payload.hanzi || typeof payload.hanzi !== "string") {
    return "hanzi is required";
  }
  if (!payload.pinyin || typeof payload.pinyin !== "string") {
    return "pinyin is required";
  }
  const difficulty = Number(payload.difficulty || 1);
  if (!Number.isInteger(difficulty) || difficulty < 1 || difficulty > 5) {
    return "difficulty must be an integer between 1 and 5";
  }
  return null;
}

function validateAnnotationPayload(payload, options = { requirePracticeRecordId: true }) {
  if (options.requirePracticeRecordId && (!payload.practiceRecordId || typeof payload.practiceRecordId !== "string")) {
    return "practiceRecordId is required";
  }
  const allowedTypes = new Set(["initial", "final", "tone", "fluency", "pronunciation", "other"]);
  if (!allowedTypes.has(payload.errorType)) {
    return "errorType must be one of initial, final, tone, fluency, pronunciation, other";
  }
  return null;
}
