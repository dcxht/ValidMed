import { useState, useEffect, useCallback, useRef } from "react";
import neuroQuestions from "../data/neuroQuestions";

const STORAGE_KEY = "validmed_q_state";
const SWIPE_THRESHOLD = 60;

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
  const [missed, setMissed] = useState([]);
  const [done, setDone] = useState(false);
  const [showCatPicker, setShowCatPicker] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);
  const [reviewRevealed, setReviewRevealed] = useState({});
  const [swipeX, setSwipeX] = useState(0);
  const [swiping, setSwiping] = useState(false);
  const touchRef = useRef({ startX: 0, startY: 0, locked: false });

  // Init from storage or fresh
  useEffect(() => {
    const saved = loadState();
    if (saved && saved.queue && saved.queue.length > 0) {
      setQueue(saved.queue);
      setCurrent(saved.current || 0);
      setScore(saved.score || { correct: 0, wrong: 0 });
      setMissed(saved.missed || []);
      setCategory(saved.category || "All");
      setDone(saved.current >= saved.queue.length);
    } else {
      startNew("All");
    }
  }, []);

  // Save on change
  useEffect(() => {
    if (queue.length > 0) {
      saveState({ queue, current, score, missed, category });
    }
  }, [queue, current, score, missed, category]);

  const startNew = useCallback((cat) => {
    const pool = cat === "All" ? neuroQuestions : neuroQuestions.filter((q) => q.category === cat);
    const shuffled = shuffle(pool);
    setQueue(shuffled);
    setCurrent(0);
    setScore({ correct: 0, wrong: 0 });
    setMissed([]);
    setRevealed(false);
    setDone(false);
    setCategory(cat);
    setShowCatPicker(false);
    setReviewMode(false);
    setReviewRevealed({});
  }, []);

  const retryMissed = useCallback(() => {
    const shuffled = shuffle(missed);
    setQueue(shuffled);
    setCurrent(0);
    setScore({ correct: 0, wrong: 0 });
    setMissed([]);
    setRevealed(false);
    setDone(false);
    setReviewMode(false);
    setReviewRevealed({});
  }, [missed]);

  const q = queue[current];
  const total = queue.length;
  const pct = total > 0 ? Math.round(((score.correct + score.wrong) / total) * 100) : 0;

  const handleMark = (correct) => {
    if (!correct) {
      setMissed((prev) => [...prev, queue[current]]);
    }
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

  // Swipe handlers (only active after answer is revealed)
  const onTouchStart = useCallback((e) => {
    const t = e.touches[0];
    touchRef.current = { startX: t.clientX, startY: t.clientY, locked: false };
    setSwiping(false);
    setSwipeX(0);
  }, []);

  const onTouchMove = useCallback((e) => {
    if (!revealed || done) return;
    const t = e.touches[0];
    const dx = t.clientX - touchRef.current.startX;
    const dy = t.clientY - touchRef.current.startY;
    // Lock direction on first significant movement
    if (!touchRef.current.locked) {
      if (Math.abs(dx) > 8 || Math.abs(dy) > 8) {
        touchRef.current.locked = true;
        touchRef.current.horizontal = Math.abs(dx) > Math.abs(dy);
      } else return;
    }
    if (touchRef.current.horizontal) {
      e.preventDefault();
      setSwiping(true);
      setSwipeX(dx);
    }
  }, [revealed, done]);

  const onTouchEnd = useCallback(() => {
    if (!revealed || done || !swiping) {
      setSwipeX(0);
      setSwiping(false);
      return;
    }
    if (swipeX > SWIPE_THRESHOLD) {
      handleMark(true); // swipe right = got it
    } else if (swipeX < -SWIPE_THRESHOLD) {
      handleMark(false); // swipe left = missed
    }
    setSwipeX(0);
    setSwiping(false);
  }, [revealed, done, swiping, swipeX]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (reviewMode) return;
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
  }, [revealed, done, current, total, reviewMode]);

  // Review missed list
  if (reviewMode && missed.length > 0) {
    return (
      <div className="q-container">
        <div className="q-review-header">
          <h2>Missed Questions ({missed.length})</h2>
          <button className="q-btn q-btn-secondary" onClick={() => setReviewMode(false)} style={{ width: "auto", padding: "6px 14px", fontSize: 13 }}>
            Back
          </button>
        </div>
        <div className="q-review-list">
          {missed.map((item, i) => {
            const isOpen = reviewRevealed[i];
            return (
              <div key={i} className="q-review-card" onClick={() => setReviewRevealed((prev) => ({ ...prev, [i]: !prev[i] }))}>
                <div className="q-review-meta">
                  <span className="q-cat-badge">{item.category}</span>
                  <span className="q-review-num">#{i + 1}</span>
                </div>
                <div className="q-review-q">{item.q}</div>
                {isOpen && (
                  <div className="q-answer-block">
                    <div className="q-divider-line" />
                    <div className="q-answer">{item.a}</div>
                  </div>
                )}
                {!isOpen && <div className="q-tap-hint" style={{ marginTop: 8 }}>Tap to reveal</div>}
              </div>
            );
          })}
        </div>
        <button className="q-btn q-btn-primary" onClick={retryMissed} style={{ marginTop: 16 }}>
          Retry Missed Only ({missed.length})
        </button>
      </div>
    );
  }

  // Done screen
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
          {missed.length > 0 && (
            <>
              <button className="q-btn q-btn-miss-review" onClick={() => setReviewMode(true)}>
                Review Missed ({missed.length})
              </button>
              <button className="q-btn q-btn-retry" onClick={retryMissed} style={{ marginTop: 8 }}>
                Retry Missed Only
              </button>
            </>
          )}
          <button className="q-btn q-btn-primary" onClick={() => startNew(category)} style={{ marginTop: 8 }}>
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
          {missed.length > 0 && (
            <button className="q-missed-btn" onClick={() => setReviewMode(true)}>
              {missed.length} missed
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="q-progress-track">
        <div className="q-progress-fill" style={{ width: `${pct}%` }} />
      </div>

      {/* Card */}
      <div
        className={`q-card ${swiping && swipeX > SWIPE_THRESHOLD ? "q-card-right" : ""} ${swiping && swipeX < -SWIPE_THRESHOLD ? "q-card-left" : ""}`}
        onClick={() => !revealed && !swiping && setRevealed(true)}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        style={swiping ? { transform: `translateX(${swipeX * 0.4}px) rotate(${swipeX * 0.03}deg)`, transition: "none" } : {}}
      >
        {swiping && Math.abs(swipeX) > SWIPE_THRESHOLD && (
          <div className={`q-swipe-label ${swipeX > 0 ? "q-swipe-right" : "q-swipe-left"}`}>
            {swipeX > 0 ? "Got it" : "Missed"}
          </div>
        )}
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

      {/* Swipe hint */}
      {revealed && !swiping && (
        <div className="q-swipe-hint">or swipe right = got it, left = missed</div>
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
