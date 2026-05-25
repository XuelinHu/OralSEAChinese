CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS app_user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'learner',
    native_language VARCHAR(64),
    country VARCHAR(64) DEFAULT 'Malaysia',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS course (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(128) NOT NULL,
    description TEXT,
    level_code VARCHAR(32) NOT NULL DEFAULT 'beginner',
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lesson (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES course(id) ON DELETE CASCADE,
    title VARCHAR(128) NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS corpus_item (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID REFERENCES lesson(id) ON DELETE SET NULL,
    item_type VARCHAR(16) NOT NULL CHECK (item_type IN ('pinyin', 'word', 'sentence')),
    hanzi TEXT NOT NULL,
    pinyin TEXT NOT NULL,
    translation_en TEXT,
    difficulty INTEGER NOT NULL DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    target_initial VARCHAR(16),
    target_final VARCHAR(16),
    target_tone VARCHAR(16),
    tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audio_asset (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corpus_item_id UUID REFERENCES corpus_item(id) ON DELETE CASCADE,
    owner_user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
    audio_type VARCHAR(32) NOT NULL CHECK (audio_type IN ('standard', 'learner')),
    storage_path TEXT NOT NULL,
    mime_type VARCHAR(64) NOT NULL DEFAULT 'audio/wav',
    duration_ms INTEGER,
    sample_rate INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS practice_record (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    corpus_item_id UUID NOT NULL REFERENCES corpus_item(id) ON DELETE CASCADE,
    learner_audio_id UUID REFERENCES audio_asset(id) ON DELETE SET NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'submitted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pronunciation_score (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    practice_record_id UUID NOT NULL REFERENCES practice_record(id) ON DELETE CASCADE,
    model_version VARCHAR(64) NOT NULL DEFAULT 'mock-v1',
    overall_score NUMERIC(5,2) NOT NULL,
    accuracy_score NUMERIC(5,2) NOT NULL,
    fluency_score NUMERIC(5,2) NOT NULL,
    tone_score NUMERIC(5,2) NOT NULL,
    feedback JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS corpus_annotation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    practice_record_id UUID NOT NULL REFERENCES practice_record(id) ON DELETE CASCADE,
    annotator_user_id UUID REFERENCES app_user(id) ON DELETE SET NULL,
    error_type VARCHAR(64) NOT NULL,
    note TEXT,
    start_ms INTEGER,
    end_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_version (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_code VARCHAR(64) NOT NULL UNIQUE,
    model_type VARCHAR(64) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_training_task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    dataset_filter JSONB NOT NULL DEFAULT '{}'::JSONB,
    result JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
