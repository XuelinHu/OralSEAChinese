INSERT INTO app_user (id, username, password_hash, display_name, role, native_language, country)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'demo_learner', 'dev-password-hash', 'Demo Learner', 'learner', 'Malay', 'Malaysia')
ON CONFLICT DO NOTHING;

INSERT INTO course (id, title, description, level_code, sort_order, is_published)
VALUES
    ('11111111-1111-1111-1111-111111111111', '中文发音入门', '面向马来西亚学习者的拼音、词语和句子发音练习。', 'beginner', 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO lesson (id, course_id, title, description, sort_order)
VALUES
    ('22222222-2222-2222-2222-222222222221', '11111111-1111-1111-1111-111111111111', '声调基础', '练习普通话四声与轻声。', 1),
    ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', '常用词语', '练习日常交流高频词语。', 2),
    ('22222222-2222-2222-2222-222222222223', '11111111-1111-1111-1111-111111111111', '日常句子', '练习完整句子的连读、停顿和语调。', 3)
ON CONFLICT DO NOTHING;

INSERT INTO corpus_item (id, lesson_id, item_type, hanzi, pinyin, translation_en, difficulty, target_tone, tags)
VALUES
    ('33333333-3333-3333-3333-333333333331', '22222222-2222-2222-2222-222222222221', 'pinyin', '妈', 'mā', 'mother', 1, '1', ARRAY['tone-1']),
    ('33333333-3333-3333-3333-333333333332', '22222222-2222-2222-2222-222222222221', 'pinyin', '马', 'mǎ', 'horse', 1, '3', ARRAY['tone-3']),
    ('33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', 'word', '你好', 'nǐ hǎo', 'hello', 1, '3-3', ARRAY['word', 'greeting']),
    ('33333333-3333-3333-3333-333333333334', '22222222-2222-2222-2222-222222222222', 'word', '谢谢', 'xiè xie', 'thank you', 1, '4-0', ARRAY['word', 'daily']),
    ('33333333-3333-3333-3333-333333333335', '22222222-2222-2222-2222-222222222223', 'sentence', '我想学习中文。', 'wǒ xiǎng xué xí zhōng wén.', 'I want to learn Chinese.', 2, '3-3-2-2-1-2', ARRAY['sentence', 'learning']),
    ('33333333-3333-3333-3333-333333333336', '22222222-2222-2222-2222-222222222223', 'sentence', '今天的天气很好。', 'jīn tiān de tiān qì hěn hǎo.', 'The weather is good today.', 2, '1-1-0-1-4-3-3', ARRAY['sentence', 'daily'])
ON CONFLICT DO NOTHING;

INSERT INTO model_version (version_code, model_type, description, is_active)
VALUES ('mock-v1', 'pronunciation-evaluator', '规则占位版发音评分，用于跑通第一阶段业务闭环。', TRUE)
ON CONFLICT DO NOTHING;
