import { useState, useEffect, useCallback } from "react";
import neuroQuestions from "../data/neuroQuestions";

const STORAGE_KEY = "validmed_q_state";

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
}

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {}
}

const categories = ["All", ...Array.from(new Set(neuroQuestions.map((q) => q.category))).sort()];

export default function Questions() {
  const [category, setCategory] = useState("All");
  const [queue, setQueue] = useState([]);
  const [current, setCurrent] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore] = useState({ correct: 0, wrong: 0 });
  const [done, setDone] = useState(false);
  const [showCatPicker, setShowCatPicker] = useState(false);

  // Init from storage or fresh
  useEffect(() => {
    const saved = loadState();
    if (saved && saved.queue && saved.queue.length > 0) {
      setQueue(saved.queue);
      setCurrent(saved.current || 0);
      setScore(saved.score || { correct: 0, wrong: 0 });
      setCategory(saved.category || "All");
      setDone(saved.current >= saved.queue.length);
    } else {
      startNew("All");
    }
  }, []);

  // Save on change
  useEffect(() => {
    if (queue.length > 0) {
      saveState({ queue, current, score, category });
    }
  }, [queue, current, score, category]);

  const startNew = useCallback((cat) => {
    const pool = cat === "All" ? neuroQuestions : neuroQuestions.filter((q) => q.category === cat);
    const shuffled = shuffle(pool);
    setQueue(shuffled);
    setCurrent(0);
    setScore({ correct: 0, wrong: 0 });
    setRevealed(false);
    setDone(false);
    setCategory(cat);
    setShowCatPicker(false);
  }, []);

  const q = queue[current];
  const total = queue.length;
  const pct = total > 0 ? Math.round(((score.correct + score.wrong) / total) * 100) : 0;

  const handleMark = (correct) => {
    setScore((s) => ({
      correct: s.correct + (correct ? 1 : 0),
      wrong: s.wrong + (correct ? 0 : 1),
    }));
    const next = current + 1;
    if (next >= total) {
      setCurrent(next);
      setDone(true);
    } else {
      setCurrent(next);
      setRevealed(false);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        if (!revealed && !done) setRevealed(true);
      }
      if (revealed && !done) {
        if (e.key === "ArrowRight" || e.key === "j") handleMark(true);
        if (e.key === "ArrowLeft" || e.key === "k") handleMark(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [revealed, done, current, total]);

  if (done) {
    const pctCorrect = score.correct + score.wrong > 0
      ? Math.round((score.correct / (score.correct + score.wrong)) * 100)
      : 0;
    return (
      <div className="q-container">
        <div className="q-done-card">
          <h2>Session Complete</h2>
          <div className="q-done-stats">
            <div className="q-done-stat">
              <span className="q-done-num q-green">{score.correct}</span>
              <span className="q-done-label">Got it</span>
            </div>
            <div className="q-done-stat">
              <span className="q-done-num q-red">{score.wrong}</span>
              <span className="q-done-label">Missed</span>
            </div>
            <div className="q-done-stat">
              <span className="q-done-num">{pctCorrect}%</span>
              <span className="q-done-label">Score</span>
            </div>
          </div>
          <button className="q-btn q-btn-primary" onClick={() => startNew(category)}>
            Restart {category === "All" ? "All" : category}
          </button>
          <button className="q-btn q-btn-secondary" onClick={() => setShowCatPicker(true)} style={{ marginTop: 8 }}>
            Pick Category
          </button>
          {showCatPicker && (
            <div className="q-cat-grid">
              {categories.map((c) => (
                <button key={c} className={`q-cat-chip ${c === category ? "q-cat-active" : ""}`} onClick={() => startNew(c)}>
                  {c} {c !== "All" && <span className="q-cat-count">({neuroQuestions.filter((x) => x.category === c).length})</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!q) return null;

  return (
    <div className="q-container">
      {/* Top bar */}
      <div className="q-topbar">
        <div className="q-progress-info">
          <span className="q-counter">{current + 1} / {total}</span>
          <span className="q-cat-badge">{q.category}</span>
        </div>
        <div className="q-score-row">
          <span className="q-green">{score.correct}</span>
          <span className="q-divider">/</span>
          <span className="q-red">{score.wrong}</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="q-progress-track">
        <div className="q-progress-fill" style={{ width: `${pct}%` }} />
      </div>

      {/* Card */}
      <div className="q-card" onClick={() => !revealed && setRevealed(true)}>
        <div className="q-question">{q.q}</div>

        {revealed ? (
          <div className="q-answer-block">
            <div className="q-divider-line" />
            <div className="q-answer">{q.a}</div>
          </div>
        ) : (
          <div className="q-tap-hint">Tap to reveal answer</div>
        )}
      </div>

      {/* Action buttons */}
      {revealed && (
        <div className="q-actions">
          <button className="q-btn q-btn-miss" onClick={() => handleMark(false)}>
            Missed it
          </button>
          <button className="q-btn q-btn-got" onClick={() => handleMark(true)}>
            Got it
          </button>
        </div>
      )}

      {/* Category picker */}
      <button className="q-change-cat" onClick={() => setShowCatPicker((v) => !v)}>
        {showCatPicker ? "Close" : "Change Category"}
      </button>
      {showCatPicker && (
        <div className="q-cat-grid">
          {categories.map((c) => (
            <button key={c} className={`q-cat-chip ${c === category ? "q-cat-active" : ""}`} onClick={() => startNew(c)}>
              {c} {c !== "All" && <span className="q-cat-count">({neuroQuestions.filter((x) => x.category === c).length})</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
