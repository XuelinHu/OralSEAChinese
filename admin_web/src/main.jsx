import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BookOpen, Database, Plus, RefreshCw, Save, Trash2 } from 'lucide-react';
import './styles.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:3100';
const emptyForm = {
  type: 'word',
  hanzi: '',
  pinyin: '',
  translationEn: '',
  difficulty: 1,
  tags: '',
  lessonId: '',
};

const emptyCourseForm = {
  title: '',
  description: '',
  levelCode: 'beginner',
  sortOrder: 1,
};

const emptyLessonForm = {
  title: '',
  description: '',
  sortOrder: 1,
};

function App() {
  const [type, setType] = useState('all');
  const [items, setItems] = useState([]);
  const [scores, setScores] = useState([]);
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [courseForm, setCourseForm] = useState(emptyCourseForm);
  const [lessonForm, setLessonForm] = useState(emptyLessonForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('等待加载');

  const filteredCount = useMemo(() => items.length, [items]);

  async function loadData(nextType = type) {
    setLoading(true);
    try {
      const query = nextType === 'all' ? '' : `?type=${nextType}`;
      const [corpusRes, scoresRes, coursesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/admin/corpus${query}`),
        fetch(`${API_BASE_URL}/api/v1/admin/practice-scores?limit=20`),
        fetch(`${API_BASE_URL}/api/v1/admin/courses`),
      ]);
      if (!corpusRes.ok) throw new Error(`语料加载失败：${corpusRes.status}`);
      if (!scoresRes.ok) throw new Error(`评分加载失败：${scoresRes.status}`);
      if (!coursesRes.ok) throw new Error(`课程加载失败：${coursesRes.status}`);
      const corpusData = await corpusRes.json();
      const scoreData = await scoresRes.json();
      const courseData = await coursesRes.json();
      setItems(corpusData.items || []);
      setScores(scoreData.items || []);
      setCourses(courseData.items || []);
      const courseId = selectedCourseId || courseData.items?.[0]?.id || '';
      if (courseId) {
        setSelectedCourseId(courseId);
        await loadLessons(courseId);
      }
      setStatus(`已加载 ${corpusData.items?.length || 0} 条语料`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadLessons(courseId) {
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/courses/${courseId}/lessons`);
    if (!response.ok) throw new Error(`课时加载失败：${response.status}`);
    const data = await response.json();
    setLessons(data.items || []);
  }

  useEffect(() => {
    loadData('all');
  }, []);

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateCourseForm(field, value) {
    setCourseForm((current) => ({ ...current, [field]: value }));
  }

  function updateLessonForm(field, value) {
    setLessonForm((current) => ({ ...current, [field]: value }));
  }

  function startEdit(item) {
    setEditingId(item.id);
    setForm({
      type: item.type,
      hanzi: item.hanzi,
      pinyin: item.pinyin,
      translationEn: item.translationEn || '',
      difficulty: item.difficulty || 1,
      tags: (item.tags || []).join(', '),
      lessonId: item.lessonId || '',
    });
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function submitForm(event) {
    event.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        difficulty: Number(form.difficulty),
        tags: form.tags,
      };
      const url = editingId
        ? `${API_BASE_URL}/api/v1/admin/corpus/${editingId}`
        : `${API_BASE_URL}/api/v1/admin/corpus`;
      const response = await fetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || `保存失败：${response.status}`);
      }
      resetForm();
      await loadData(type);
      setStatus(editingId ? '语料已更新' : '语料已新增');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitCourse(event) {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/courses`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ ...courseForm, sortOrder: Number(courseForm.sortOrder), isPublished: true }),
      });
      if (!response.ok) throw new Error(`课程保存失败：${response.status}`);
      setCourseForm(emptyCourseForm);
      await loadData(type);
      setStatus('课程已新增');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitLesson(event) {
    event.preventDefault();
    if (!selectedCourseId) {
      setStatus('请先选择课程');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/lessons`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          ...lessonForm,
          courseId: selectedCourseId,
          sortOrder: Number(lessonForm.sortOrder),
        }),
      });
      if (!response.ok) throw new Error(`课时保存失败：${response.status}`);
      setLessonForm(emptyLessonForm);
      await loadLessons(selectedCourseId);
      setStatus('课时已新增');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteItem(item) {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/corpus/${item.id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`删除失败：${response.status}`);
      await loadData(type);
      setStatus('语料已删除');
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  function changeType(nextType) {
    setType(nextType);
    loadData(nextType);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Database size={24} />
          <div>
            <strong>OralSEA Chinese</strong>
            <span>语料管理后台</span>
          </div>
        </div>
        <nav>
          <button className="nav-active">语料库</button>
          <button>课程课时</button>
          <button>评分记录</button>
          <button>模型任务</button>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>中文发音语料</h1>
            <p>管理拼音、词语和句子练习内容</p>
          </div>
          <button className="icon-button" onClick={() => loadData(type)} disabled={loading} title="刷新">
            <RefreshCw size={18} />
          </button>
        </header>

        <section className="toolbar">
          {['all', 'pinyin', 'word', 'sentence'].map((value) => (
            <button
              key={value}
              className={type === value ? 'seg-active' : ''}
              onClick={() => changeType(value)}
            >
              {typeLabel(value)}
            </button>
          ))}
          <span>{filteredCount} 条</span>
          <span>{status}</span>
        </section>

        <section className="content-grid">
          <section className="editor-panel">
            <div className="panel-title">
              <BookOpen size={18} />
              <h2>课程课时</h2>
            </div>
            <form className="inline-form" onSubmit={submitCourse}>
              <label>
                课程名称
                <input value={courseForm.title} onChange={(event) => updateCourseForm('title', event.target.value)} required />
              </label>
              <label>
                说明
                <input value={courseForm.description} onChange={(event) => updateCourseForm('description', event.target.value)} />
              </label>
              <button className="primary" type="submit" disabled={loading}>新增课程</button>
            </form>
            <label>
              当前课程
              <select
                value={selectedCourseId}
                onChange={async (event) => {
                  setSelectedCourseId(event.target.value);
                  await loadLessons(event.target.value);
                }}
              >
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>{course.title}</option>
                ))}
              </select>
            </label>
            <form className="inline-form" onSubmit={submitLesson}>
              <label>
                课时名称
                <input value={lessonForm.title} onChange={(event) => updateLessonForm('title', event.target.value)} required />
              </label>
              <label>
                说明
                <input value={lessonForm.description} onChange={(event) => updateLessonForm('description', event.target.value)} />
              </label>
              <button className="primary" type="submit" disabled={loading}>新增课时</button>
            </form>
            <div className="lesson-list">
              {lessons.map((lesson) => (
                <button key={lesson.id} type="button" onClick={() => updateForm('lessonId', lesson.id)}>
                  {lesson.title}
                </button>
              ))}
            </div>
          </section>

          <form className="editor-panel" onSubmit={submitForm}>
            <div className="panel-title">
              <Plus size={18} />
              <h2>{editingId ? '编辑语料' : '新增语料'}</h2>
            </div>
            <label>
              归属课时
              <select value={form.lessonId} onChange={(event) => updateForm('lessonId', event.target.value)}>
                <option value="">不指定</option>
                {lessons.map((lesson) => (
                  <option key={lesson.id} value={lesson.id}>{lesson.title}</option>
                ))}
              </select>
            </label>
            <label>
              类型
              <select value={form.type} onChange={(event) => updateForm('type', event.target.value)}>
                <option value="pinyin">拼音</option>
                <option value="word">词语</option>
                <option value="sentence">句子</option>
              </select>
            </label>
            <label>
              汉字
              <input value={form.hanzi} onChange={(event) => updateForm('hanzi', event.target.value)} required />
            </label>
            <label>
              拼音
              <input value={form.pinyin} onChange={(event) => updateForm('pinyin', event.target.value)} required />
            </label>
            <label>
              英文释义
              <input value={form.translationEn} onChange={(event) => updateForm('translationEn', event.target.value)} />
            </label>
            <label>
              难度
              <input
                type="number"
                min="1"
                max="5"
                value={form.difficulty}
                onChange={(event) => updateForm('difficulty', event.target.value)}
              />
            </label>
            <label>
              标签
              <input value={form.tags} onChange={(event) => updateForm('tags', event.target.value)} />
            </label>
            <div className="form-actions">
              <button className="primary" type="submit" disabled={loading}>
                <Save size={16} />
                保存
              </button>
              <button type="button" onClick={resetForm}>清空</button>
            </div>
          </form>

          <section className="table-panel">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>类型</th>
                    <th>汉字</th>
                    <th>拼音</th>
                    <th>释义</th>
                    <th>难度</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.id}>
                      <td><span className={`type-pill type-${item.type}`}>{typeLabel(item.type)}</span></td>
                      <td>{item.hanzi}</td>
                      <td>{item.pinyin}</td>
                      <td>{item.translationEn}</td>
                      <td>{item.difficulty}</td>
                      <td className="row-actions">
                        <button onClick={() => startEdit(item)}>编辑</button>
                        <button className="danger" onClick={() => deleteItem(item)} title="删除">
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </section>

        <section className="scores-panel">
          <h2>最近评分记录</h2>
          {scores.length === 0 ? (
            <p>暂无 PostgreSQL 评分记录；无数据库模式下这里为空。</p>
          ) : (
            <div className="score-list">
              {scores.map((score) => (
                <div key={score.practiceRecordId} className="score-item">
                  <strong>{score.hanzi}</strong>
                  <span>{score.pinyin}</span>
                  <b>{score.overallScore.toFixed(1)}</b>
                </div>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function typeLabel(value) {
  return {
    all: '全部',
    pinyin: '拼音',
    word: '词语',
    sentence: '句子',
  }[value] || value;
}

createRoot(document.getElementById('root')).render(<App />);
