import { useState, useEffect, useCallback, useRef } from "react";
import neuroQuestions from "../data/neuroQuestions";
import endoPathQuestions from "../data/endoPathQuestions";
import renalPulmQuestions from "../data/renalPulmQuestions";
import biochemQuestions from "../data/biochemQuestions";
import arrowsQuestions from "../data/arrowsQuestions";

const BANKS = {
  neuro: { label: "Neuro", questions: neuroQuestions },
  endopath: { label: "Endo + Path", questions: endoPathQuestions },
  renalpulm: { label: "Renal + Pulm", questions: renalPulmQuestions },
  biochem: { label: "Biochem", questions: biochemQuestions },
  arrows: { label: "Arrows", questions: arrowsQuestions },
};
const DEFAULT_BANK = "endopath";
const SWIPE_THRESHOLD = 60;

function storageKey(bank) { return `validmed_q_${bank}`; }

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function loadState(bank) {
  try {
    const raw = localStorage.getItem(storageKey(bank));
    if (raw) return JSON.parse(raw);
  } catch {}
  return null;
}

function saveState(bank, state) {
  try {
    localStorage.setItem(storageKey(bank), JSON.stringify(state));
  } catch {}
}

function getCategories(bank) {
  const qs = BANKS[bank].questions;
  return ["All", ...Array.from(new Set(qs.map((q) => q.category))).sort()];
}

export default function Questions() {
  const [bank, setBank] = useState(DEFAULT_BANK);
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

  const categories = getCategories(bank);

  // Init from storage or fresh
  useEffect(() => {
    const saved = loadState(bank);
    if (saved && saved.queue && saved.queue.length > 0) {
      setQueue(saved.queue);
      setCurrent(saved.current || 0);
      setScore(saved.score || { correct: 0, wrong: 0 });
      setMissed(saved.missed || []);
      setCategory(saved.category || "All");
      setDone(saved.current >= saved.queue.length);
    } else {
      startNew("All", bank);
    }
  }, [bank]);

  // Save on change
  useEffect(() => {
    if (queue.length > 0) {
      saveState(bank, { queue, current, score, missed, category });
    }
  }, [queue, current, score, missed, category, bank]);

  const startNew = useCallback((cat, b) => {
    const currentBank = b || bank;
    const allQs = BANKS[currentBank].questions;
    const pool = cat === "All" ? allQs : allQs.filter((q) => q.category === cat);
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
  }, [bank]);

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
  // Swipe handlers are attached natively with { passive: false }: React attaches
  // touchmove passively at the root, so preventDefault() from a JSX onTouchMove is
  // ignored and the browser keeps the gesture (page pan / overscroll) instead.
  const detachRef = useRef(null);
  const EDGE_DEAD_ZONE = 28; // leave iOS Safari's back-swipe strip alone

  // Latest state for the native listeners, so they can be bound once and never
  // rebind mid-gesture (a rebind can make later touchmove events non-cancelable).
  const liveRef = useRef({ revealed, done, handleMark });
  liveRef.current = { revealed, done, handleMark };

  // Callback ref: the card only mounts once a question is loaded, so binding in a
  // plain effect on first render would miss it.
  const cardRef = useCallback((el) => {
    if (detachRef.current) {
      detachRef.current();
      detachRef.current = null;
    }
    if (!el) return;

    const onStart = (e) => {
      const t = e.touches[0];
      const fromEdge = t.clientX < EDGE_DEAD_ZONE || t.clientX > window.innerWidth - EDGE_DEAD_ZONE;
      touchRef.current = { startX: t.clientX, startY: t.clientY, locked: fromEdge, horizontal: false };
      setSwiping(false);
      setSwipeX(0);
    };

    const onMove = (e) => {
      const { revealed: isRevealed, done: isDone } = liveRef.current;
      if (!isRevealed || isDone) return;
      const ref = touchRef.current;
      if (!ref) return;
      const t = e.touches[0];
      const dx = t.clientX - ref.startX;
      const dy = t.clientY - ref.startY;
      if (!ref.locked) {
        if (Math.abs(dx) < 12 && Math.abs(dy) < 12) return;
        ref.locked = true;
        ref.horizontal = Math.abs(dx) > Math.abs(dy) * 1.5;
      }
      if (!ref.horizontal) return;
      if (e.cancelable) e.preventDefault();
      ref.dx = dx;
      setSwiping(true);
      setSwipeX(dx);
    };

    const onEnd = () => {
      const ref = touchRef.current;
      touchRef.current = null;
      const { revealed: isRevealed, done: isDone, handleMark: mark } = liveRef.current;
      if (!isRevealed || isDone || !ref || !ref.horizontal) {
        setSwipeX(0);
        setSwiping(false);
        return;
      }
      const dx = ref.dx || 0;
      setSwipeX(0);
      setSwiping(false);
      if (dx > SWIPE_THRESHOLD) mark(true);
      else if (dx < -SWIPE_THRESHOLD) mark(false);
    };

    el.addEventListener("touchstart", onStart, { passive: true });
    el.addEventListener("touchmove", onMove, { passive: false });
    el.addEventListener("touchend", onEnd, { passive: true });
    el.addEventListener("touchcancel", onEnd, { passive: true });
    detachRef.current = () => {
      el.removeEventListener("touchstart", onStart);
      el.removeEventListener("touchmove", onMove);
      el.removeEventListener("touchend", onEnd);
      el.removeEventListener("touchcancel", onEnd);
    };
  }, []);

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
                  {c} {c !== "All" && <span className="q-cat-count">({BANKS[bank].questions.filter((x) => x.category === c).length})</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!q) return null;

  const switchBank = (b) => {
    setBank(b);
    setRevealed(false);
    setShowCatPicker(false);
    setReviewMode(false);
    setReviewRevealed({});
  };

  return (
    <div className="q-container">
      {/* Bank selector */}
      <div className="q-bank-selector" style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {Object.entries(BANKS).map(([key, val]) => (
          <button key={key} className={`q-cat-chip ${key === bank ? "q-cat-active" : ""}`} onClick={() => switchBank(key)} style={{ flex: 1 }}>
            {val.label} ({val.questions.length})
          </button>
        ))}
      </div>
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
        ref={cardRef}
        className={`q-card ${swiping && swipeX > SWIPE_THRESHOLD ? "q-card-right" : ""} ${swiping && swipeX < -SWIPE_THRESHOLD ? "q-card-left" : ""}`}
        onClick={() => !revealed && !swiping && setRevealed(true)}
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
              {c} {c !== "All" && <span className="q-cat-count">({BANKS[bank].questions.filter((x) => x.category === c).length})</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
