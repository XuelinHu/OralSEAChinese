import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Pool } from "pg";

import { config } from "./config.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const corpusPath = path.join(__dirname, "data", "corpus.json");
const corpus = JSON.parse(fs.readFileSync(corpusPath, "utf8"));

const pool = config.databaseUrl ? new Pool({ connectionString: config.databaseUrl }) : null;
const demoUserId = "00000000-0000-0000-0000-000000000001";

function hasDatabase() {
  return Boolean(pool);
}

function mapCourse(row) {
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    levelCode: row.level_code,
    lessonCount: Number(row.lesson_count || 0),
  };
}

function mapLesson(row) {
  return {
    id: row.id,
    courseId: row.course_id,
    title: row.title,
    description: row.description,
    sortOrder: row.sort_order,
  };
}

function mapCorpusItem(row) {
  return {
    id: row.id,
    lessonId: row.lesson_id,
    type: row.item_type,
    hanzi: row.hanzi,
    pinyin: row.pinyin,
    translationEn: row.translation_en || "",
    difficulty: row.difficulty,
    tags: row.tags || [],
  };
}

function normalizeTags(tags) {
  if (Array.isArray(tags)) {
    return tags.map((tag) => String(tag).trim()).filter(Boolean);
  }
  if (typeof tags === "string") {
    return tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }
  return [];
}

export async function healthCheckDatabase() {
  if (!pool) {
    return { connected: false, mode: "json-seed" };
  }
  const result = await pool.query("SELECT 1 AS ok");
  return { connected: result.rows[0].ok === 1, mode: "postgresql" };
}

export async function listCourses() {
  if (hasDatabase()) {
    const result = await pool.query(`
      SELECT
        c.id,
        c.title,
        c.description,
        c.level_code,
        COUNT(l.id) AS lesson_count
      FROM course c
      LEFT JOIN lesson l ON l.course_id = c.id
      WHERE c.is_published = TRUE
      GROUP BY c.id
      ORDER BY c.sort_order ASC, c.created_at ASC
    `);
    return result.rows.map(mapCourse);
  }

  return [
    {
      id: "11111111-1111-1111-1111-111111111111",
      title: "中文发音入门",
      description: "面向马来西亚学习者的拼音、词语和句子发音练习。",
      levelCode: "beginner",
      lessonCount: 3,
    },
  ];
}

export async function createCourse(payload) {
  const course = {
    id: crypto.randomUUID(),
    title: payload.title,
    description: payload.description || "",
    levelCode: payload.levelCode || "beginner",
    sortOrder: Number(payload.sortOrder || 0),
    isPublished: payload.isPublished ?? true,
  };

  if (hasDatabase()) {
    const result = await pool.query(
      `
        INSERT INTO course (id, title, description, level_code, sort_order, is_published)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, title, description, level_code, 0 AS lesson_count
      `,
      [course.id, course.title, course.description, course.levelCode, course.sortOrder, course.isPublished],
    );
    return mapCourse(result.rows[0]);
  }

  return { ...course, lessonCount: 0 };
}

export async function updateCourse(id, payload) {
  if (!hasDatabase()) {
    return {
      id,
      title: payload.title,
      description: payload.description || "",
      levelCode: payload.levelCode || "beginner",
      lessonCount: 3,
    };
  }

  const result = await pool.query(
    `
      UPDATE course
      SET title = $2,
          description = $3,
          level_code = $4,
          sort_order = $5,
          is_published = $6
      WHERE id = $1
      RETURNING id, title, description, level_code, 0 AS lesson_count
    `,
    [
      id,
      payload.title,
      payload.description || "",
      payload.levelCode || "beginner",
      Number(payload.sortOrder || 0),
      payload.isPublished ?? true,
    ],
  );
  return result.rows[0] ? mapCourse(result.rows[0]) : null;
}

export async function listLessons(courseId) {
  if (hasDatabase()) {
    const result = await pool.query(
      `
        SELECT id, course_id, title, description, sort_order
        FROM lesson
        WHERE course_id = $1
        ORDER BY sort_order ASC, created_at ASC
      `,
      [courseId],
    );
    return result.rows.map(mapLesson);
  }

  return [
    {
      id: "22222222-2222-2222-2222-222222222221",
      courseId,
      title: "声调基础",
      sortOrder: 1,
    },
    {
      id: "22222222-2222-2222-2222-222222222222",
      courseId,
      title: "常用词语",
      sortOrder: 2,
    },
    {
      id: "22222222-2222-2222-2222-222222222223",
      courseId,
      title: "日常句子",
      sortOrder: 3,
    },
  ];
}

export async function createLesson(payload) {
  const lesson = {
    id: crypto.randomUUID(),
    courseId: payload.courseId,
    title: payload.title,
    description: payload.description || "",
    sortOrder: Number(payload.sortOrder || 0),
  };

  if (hasDatabase()) {
    const result = await pool.query(
      `
        INSERT INTO lesson (id, course_id, title, description, sort_order)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, course_id, title, description, sort_order
      `,
      [lesson.id, lesson.courseId, lesson.title, lesson.description, lesson.sortOrder],
    );
    return mapLesson(result.rows[0]);
  }

  return lesson;
}

export async function updateLesson(id, payload) {
  if (!hasDatabase()) {
    return {
      id,
      courseId: payload.courseId,
      title: payload.title,
      description: payload.description || "",
      sortOrder: Number(payload.sortOrder || 0),
    };
  }

  const result = await pool.query(
    `
      UPDATE lesson
      SET course_id = $2,
          title = $3,
          description = $4,
          sort_order = $5
      WHERE id = $1
      RETURNING id, course_id, title, description, sort_order
    `,
    [id, payload.courseId, payload.title, payload.description || "", Number(payload.sortOrder || 0)],
  );
  return result.rows[0] ? mapLesson(result.rows[0]) : null;
}

export async function listCorpusItems(filters = {}) {
  if (hasDatabase()) {
    const conditions = [];
    const values = [];

    if (filters.type) {
      values.push(filters.type);
      conditions.push(`item_type = $${values.length}`);
    }
    if (filters.lessonId) {
      values.push(filters.lessonId);
      conditions.push(`lesson_id = $${values.length}`);
    }

    const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";
    const result = await pool.query(
      `
        SELECT id, lesson_id, item_type, hanzi, pinyin, translation_en, difficulty, tags
        FROM corpus_item
        ${where}
        ORDER BY difficulty ASC, created_at ASC
      `,
      values,
    );
    return result.rows.map(mapCorpusItem);
  }

  return corpus.filter((item) => {
    if (filters.type && item.type !== filters.type) {
      return false;
    }
    if (filters.lessonId && item.lessonId !== filters.lessonId) {
      return false;
    }
    return true;
  });
}

export async function getCorpusItem(id) {
  if (hasDatabase()) {
    const result = await pool.query(
      `
        SELECT id, lesson_id, item_type, hanzi, pinyin, translation_en, difficulty, tags
        FROM corpus_item
        WHERE id = $1
      `,
      [id],
    );
    return result.rows[0] ? mapCorpusItem(result.rows[0]) : null;
  }

  return corpus.find((item) => item.id === id) || null;
}

export async function createCorpusItem(payload) {
  const item = {
    id: crypto.randomUUID(),
    lessonId: payload.lessonId || null,
    type: payload.type,
    hanzi: payload.hanzi,
    pinyin: payload.pinyin,
    translationEn: payload.translationEn || "",
    difficulty: Number(payload.difficulty || 1),
    tags: normalizeTags(payload.tags),
  };

  if (hasDatabase()) {
    const result = await pool.query(
      `
        INSERT INTO corpus_item (
          id,
          lesson_id,
          item_type,
          hanzi,
          pinyin,
          translation_en,
          difficulty,
          tags
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id, lesson_id, item_type, hanzi, pinyin, translation_en, difficulty, tags
      `,
      [
        item.id,
        item.lessonId,
        item.type,
        item.hanzi,
        item.pinyin,
        item.translationEn,
        item.difficulty,
        item.tags,
      ],
    );
    return mapCorpusItem(result.rows[0]);
  }

  corpus.push(item);
  return item;
}

export async function updateCorpusItem(id, payload) {
  if (hasDatabase()) {
    const existing = await getCorpusItem(id);
    if (!existing) {
      return null;
    }

    const next = {
      lessonId: payload.lessonId ?? existing.lessonId,
      type: payload.type ?? existing.type,
      hanzi: payload.hanzi ?? existing.hanzi,
      pinyin: payload.pinyin ?? existing.pinyin,
      translationEn: payload.translationEn ?? existing.translationEn,
      difficulty: Number(payload.difficulty ?? existing.difficulty),
      tags: payload.tags === undefined ? existing.tags : normalizeTags(payload.tags),
    };

    const result = await pool.query(
      `
        UPDATE corpus_item
        SET lesson_id = $2,
            item_type = $3,
            hanzi = $4,
            pinyin = $5,
            translation_en = $6,
            difficulty = $7,
            tags = $8
        WHERE id = $1
        RETURNING id, lesson_id, item_type, hanzi, pinyin, translation_en, difficulty, tags
      `,
      [
        id,
        next.lessonId,
        next.type,
        next.hanzi,
        next.pinyin,
        next.translationEn,
        next.difficulty,
        next.tags,
      ],
    );
    return mapCorpusItem(result.rows[0]);
  }

  const index = corpus.findIndex((item) => item.id === id);
  if (index < 0) {
    return null;
  }
  corpus[index] = {
    ...corpus[index],
    ...payload,
    difficulty: Number(payload.difficulty ?? corpus[index].difficulty),
    tags: payload.tags === undefined ? corpus[index].tags : normalizeTags(payload.tags),
  };
  return corpus[index];
}

export async function deleteCorpusItem(id) {
  if (hasDatabase()) {
    const result = await pool.query("DELETE FROM corpus_item WHERE id = $1 RETURNING id", [id]);
    return result.rowCount > 0;
  }

  const index = corpus.findIndex((item) => item.id === id);
  if (index < 0) {
    return false;
  }
  corpus.splice(index, 1);
  return true;
}

export async function listPracticeScores(limit = 50) {
  if (!hasDatabase()) {
    return [];
  }

  const result = await pool.query(
    `
      SELECT
        pr.id AS practice_record_id,
        pr.created_at,
        ci.hanzi,
        ci.pinyin,
        ci.item_type,
        ps.model_version,
        ps.overall_score,
        ps.accuracy_score,
        ps.fluency_score,
        ps.tone_score
      FROM practice_record pr
      JOIN corpus_item ci ON ci.id = pr.corpus_item_id
      JOIN pronunciation_score ps ON ps.practice_record_id = pr.id
      ORDER BY pr.created_at DESC
      LIMIT $1
    `,
    [limit],
  );

  return result.rows.map((row) => ({
    practiceRecordId: row.practice_record_id,
    createdAt: row.created_at,
    hanzi: row.hanzi,
    pinyin: row.pinyin,
    type: row.item_type,
    modelVersion: row.model_version,
    overallScore: Number(row.overall_score),
    accuracyScore: Number(row.accuracy_score),
    fluencyScore: Number(row.fluency_score),
    toneScore: Number(row.tone_score),
  }));
}

export async function getPracticeScore(id) {
  if (!hasDatabase()) {
    return null;
  }

  const result = await pool.query(
    `
      SELECT
        pr.id AS practice_record_id,
        pr.created_at,
        aa.storage_path,
        aa.mime_type,
        aa.duration_ms,
        ci.id AS corpus_item_id,
        ci.hanzi,
        ci.pinyin,
        ci.item_type,
        ps.model_version,
        ps.overall_score,
        ps.accuracy_score,
        ps.fluency_score,
        ps.tone_score,
        ps.feedback
      FROM practice_record pr
      JOIN corpus_item ci ON ci.id = pr.corpus_item_id
      LEFT JOIN audio_asset aa ON aa.id = pr.learner_audio_id
      JOIN pronunciation_score ps ON ps.practice_record_id = pr.id
      WHERE pr.id = $1
    `,
    [id],
  );
  const row = result.rows[0];
  if (!row) return null;
  return {
    practiceRecordId: row.practice_record_id,
    createdAt: row.created_at,
    audio: {
      storagePath: row.storage_path,
      mimeType: row.mime_type,
      durationMs: row.duration_ms,
    },
    corpusItem: {
      id: row.corpus_item_id,
      hanzi: row.hanzi,
      pinyin: row.pinyin,
      type: row.item_type,
    },
    score: {
      modelVersion: row.model_version,
      overallScore: Number(row.overall_score),
      accuracyScore: Number(row.accuracy_score),
      fluencyScore: Number(row.fluency_score),
      toneScore: Number(row.tone_score),
      feedback: row.feedback,
    },
  };
}

export async function savePracticeEvaluation({ practiceRecordId, corpusItemId, audio, score }) {
  if (!hasDatabase()) {
    return { persisted: false, mode: "json-seed" };
  }

  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    let audioAssetId = null;
    if (audio?.received) {
      const audioResult = await client.query(
        `
          INSERT INTO audio_asset (
            corpus_item_id,
            owner_user_id,
            audio_type,
            storage_path,
            mime_type,
            duration_ms
          )
          VALUES ($1, $2, 'learner', $3, $4, $5)
          RETURNING id
        `,
        [
          corpusItemId,
          demoUserId,
          audio.storagePath,
          audio.mimeType || "audio/wav",
          audio.durationMs || null,
        ],
      );
      audioAssetId = audioResult.rows[0].id;
    }

    await client.query(
      `
        INSERT INTO practice_record (id, user_id, corpus_item_id, learner_audio_id, status)
        VALUES ($1, $2, $3, $4, 'scored')
      `,
      [practiceRecordId, demoUserId, corpusItemId, audioAssetId],
    );

    const scoreResult = await client.query(
      `
        INSERT INTO pronunciation_score (
          practice_record_id,
          model_version,
          overall_score,
          accuracy_score,
          fluency_score,
          tone_score,
          feedback
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
        RETURNING id
      `,
      [
        practiceRecordId,
        score.model_version,
        score.overall_score,
        score.accuracy_score,
        score.fluency_score,
        score.tone_score,
        JSON.stringify(score.feedback || []),
      ],
    );

    await client.query("COMMIT");
    return {
      persisted: true,
      mode: "postgresql",
      audioAssetId,
      scoreId: scoreResult.rows[0].id,
    };
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}
