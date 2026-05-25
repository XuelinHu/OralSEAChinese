CREATE INDEX IF NOT EXISTS idx_lesson_course_id ON lesson(course_id);
CREATE INDEX IF NOT EXISTS idx_corpus_item_lesson_id ON corpus_item(lesson_id);
CREATE INDEX IF NOT EXISTS idx_corpus_item_type ON corpus_item(item_type);
CREATE INDEX IF NOT EXISTS idx_audio_asset_corpus_item_id ON audio_asset(corpus_item_id);
CREATE INDEX IF NOT EXISTS idx_audio_asset_owner_user_id ON audio_asset(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_practice_record_user_id ON practice_record(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_record_corpus_item_id ON practice_record(corpus_item_id);
CREATE INDEX IF NOT EXISTS idx_pronunciation_score_practice_id ON pronunciation_score(practice_record_id);
