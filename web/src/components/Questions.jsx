import { useState, useEffect, useCallback, useRef } from "react";
import { BANKS } from "../data/banks";
import { recordEvent } from "../historyStore";
import { key } from "../names";

const DEFAULT_BANK = "endopath";
const MISSED_BANK = "__missed__";
const FLAG_BANK = "__flagged__";
const SWIPE_THRESHOLD = 45; // px of travel that commits a swipe
const FLICK_MIN_DIST = 25;  // px - shorter travel still commits if fast
const FLICK_MIN_VEL = 0.25; // px/ms over the last ~120ms of the gesture (250px/s = a real flick)

const ABBREV = /\b(e\.g|i\.e|vs|approx|etc|No|Fig|Dr|Mr|Mrs|Ms|St)\.$/i;

function sentences(text) {
  const parts = String(text || "").trim().split(/([.?!])\s+(?=[A-Z(\u2191\u2193\u2194])/);
  const out = [];
  for (let i = 0; i < parts.length; i += 2) {
    const seg = (parts[i] || "") + (parts[i + 1] || "");
    if (seg) out.push(seg.trim());
  }
  // re-join fragments that ended on a common abbreviation
  const merged = [];
  for (const seg of out) {
    if (merged.length && ABBREV.test(merged[merged.length - 1])) merged[merged.length - 1] += " " + seg;
    else merged.push(seg);
  }
  return merged;
}

function splitAnswer(text) {
  const sents = sentences(text);
  if (sents.length < 2 || sents[0].length > 180) return ["", String(text || "").trim()];
  return [sents[0], sents.slice(1).join(" ")];
}

function toParagraphs(text) {
  const sents = sentences(text);
  const out = [];
  let buf = "";
  for (const seg of sents) {
    buf = buf ? buf + " " + seg : seg;
    if (buf.length >= 200) {
      out.push(buf);
      buf = "";
    }
  }
  if (buf) {
    if (out.length && buf.length < 60) out[out.length - 1] += " " + buf;
    else out.push(buf);
  }
  return out;
}

function AnswerText({ text }) {
  const [lead, body] = splitAnswer(text);
  return (
    <>
      {lead && <div className="q-answer-lead">{lead}</div>}
      {toParagraphs(body).map((p, i) => (
        <p key={i} className="q-answer-body">{p}</p>
      ))}
    </>
  );
}

function storageKey(bank) { return key(`validmed_q_${bank}`); }

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

// Flags are global across banks and never auto-clear: a flagged question stays
// flagged until the user swipes up on it again.
function loadFlags() {
  try {
    const raw = localStorage.getItem(key("validmed_flags"));
    if (raw) return new Set(JSON.parse(raw));
  } catch {}
  return new Set();
}

function saveFlags(flags) {
  try {
    localStorage.setItem(key("validmed_flags"), JSON.stringify([...flags]));
  } catch {}
}

function toggleFlagId(flags, id) {
  const next = new Set(flags);
  if (next.has(id)) next.delete(id); else next.add(id);
  saveFlags(next);
  return next;
}

function getCategoryCounts(bank) {
  const counts = new Map();
  for (const q of BANKS[bank].questions) counts.set(q.category, (counts.get(q.category) || 0) + 1);
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

// Every question the user has marked wrong, across all banks, de-duplicated.
function collectMissed() {
  const seen = new Set();
  const out = [];
  for (const key of Object.keys(BANKS)) {
    const saved = loadState(key);
    for (const q of (saved && saved.missed) || []) {
      if (q && q.id && !seen.has(q.id)) {
        seen.add(q.id);
        out.push(q);
      }
    }
  }
  return out;
}

// Every flagged question, across all banks, de-duplicated.
function collectFlagged() {
  const flags = loadFlags();
  if (flags.size === 0) return [];
  const out = [];
  for (const key of Object.keys(BANKS)) {
    for (const q of BANKS[key].questions) {
      if (flags.has(q.id)) out.push(q);
    }
  }
  return out;
}

function bankLabel(bank) {
  if (bank === MISSED_BANK) return "Missed";
  if (bank === FLAG_BANK) return "Flagged";
  return BANKS[bank].label;
}

function bankProgress(bank) {
  const saved = loadState(bank);
  const total = BANKS[bank].questions.length;
  if (!saved || !saved.queue) return { total, seen: 0, correct: 0, category: "All" };
  const score = saved.score || { correct: 0, wrong: 0 };
  return {
    total,
    seen: score.correct + score.wrong,
    correct: score.correct,
    inPlay: saved.queue.length,
    category: saved.category || "All",
  };
}

export default function Questions() {
  const [bank, setBank] = useState(() => {
    try {
      const last = localStorage.getItem(key("validmed_last_bank"));
      if (last && (BANKS[last] || last === MISSED_BANK || last === FLAG_BANK)) return last;
    } catch {}
    return DEFAULT_BANK;
  });
  const [category, setCategory] = useState("All");
  const [queue, setQueue] = useState([]);
  const [current, setCurrent] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore] = useState({ correct: 0, wrong: 0 });
  const [missed, setMissed] = useState([]);
  // Per-card answers for this run: queue index -> "correct" | "wrong".
  // Lets the back button revisit a card without double-counting stats.
  const [results, setResults] = useState({});
  const [done, setDone] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [sheetBank, setSheetBank] = useState(null);
  const [catQuery, setCatQuery] = useState("");
  const pendingRef = useRef(null);
  const [reviewMode, setReviewMode] = useState(false);
  const [reviewRevealed, setReviewRevealed] = useState({});
  const [swipeX, setSwipeX] = useState(0);
  const [swiping, setSwiping] = useState(false);
  const [flags, setFlags] = useState(loadFlags);
  const [flagFlash, setFlagFlash] = useState(null);
  const touchRef = useRef({ startX: 0, startY: 0, locked: false });


  // Init from storage or fresh
  useEffect(() => {
    try { localStorage.setItem(key("validmed_last_bank"), bank); } catch {}
    const pending = pendingRef.current;
    if (pending && pending.bank === bank) {
      pendingRef.current = null;
      startNew(pending.category, bank);
      return;
    }
    const saved = loadState(bank);
    if (saved && saved.queue && saved.queue.length > 0) {
      setQueue(saved.queue);
      setCurrent(saved.current || 0);
      setScore(saved.score || { correct: 0, wrong: 0 });
      setMissed(saved.missed || []);
      setResults(saved.results || {});
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
    const allQs = currentBank === MISSED_BANK ? collectMissed() : currentBank === FLAG_BANK ? collectFlagged() : BANKS[currentBank].questions;
    const pool = cat === "All" ? allQs : allQs.filter((q) => q.category === cat);
    const shuffled = shuffle(pool);
    setQueue(shuffled);
    setCurrent(0);
    setScore({ correct: 0, wrong: 0 });
    setMissed([]);
    setResults({});
    setRevealed(false);
    setDone(false);
    setCategory(cat);
    setReviewMode(false);
    setReviewRevealed({});
  }, [bank]);

  const retryMissed = useCallback(() => {
    const shuffled = shuffle(missed);
    setQueue(shuffled);
    setCurrent(0);
    setScore({ correct: 0, wrong: 0 });
    setMissed([]);
    setResults({});
    setRevealed(false);
    setDone(false);
    setReviewMode(false);
    setReviewRevealed({});
  }, [missed]);

  const q = queue[current];
  const total = queue.length;
  const pct = total > 0 ? Math.round(((score.correct + score.wrong) / total) * 100) : 0;

  const toggleFlag = () => {
    const item = queue[current];
    if (!item || !item.id) return;
    setFlags((prev) => {
      const next = toggleFlagId(prev, item.id);
      recordEvent({ type: "flag", id: item.id, bank, flagged: next.has(item.id) });
      setFlagFlash(next.has(item.id) ? "Flagged" : "Unflagged");
      setTimeout(() => setFlagFlash(null), 700);
      return next;
    });
  };

  const handleMark = (correct) => {
    const item = queue[current];
    const val = correct ? "correct" : "wrong";
    const prevResult = item ? results[current] : undefined;
    if (!prevResult) {
      // First answer for this card: full count.
      if (item && item.id) recordEvent({ type: "mark", id: item.id, bank, correct });
      if (!correct && item) setMissed((prev) => [...prev, item]);
      setScore((s) => ({
        correct: s.correct + (correct ? 1 : 0),
        wrong: s.wrong + (correct ? 0 : 1),
      }));
    } else if (prevResult !== val) {
      // Answer change on a revisited card: re-tally, never double-count.
      setScore((s) => ({
        correct: s.correct + (correct ? 1 : -1),
        wrong: s.wrong + (correct ? -1 : 1),
      }));
      if (correct) {
        setMissed((prev) =>
          item && item.id ? prev.filter((m) => m.id !== item.id) : prev.slice(0, -1)
        );
      } else if (item) {
        setMissed((prev) =>
          item.id && prev.some((m) => m.id === item.id) ? prev : [...prev, item]
        );
      }
    }
    setResults((r) => ({ ...r, [current]: val }));
    const next = current + 1;
    if (next >= total) {
      setCurrent(next);
      setDone(true);
    } else {
      setCurrent(next);
      setRevealed(!!results[next]);
    }
  };

  // Back one card. The revisited card keeps its recorded answer: it shows
  // revealed with its choice highlighted, and re-marking re-tallies instead
  // of double-counting. From the done screen, back returns to the last card.
  const canBack = done ? total > 0 : current > 0;
  const handleBack = () => {
    if (!canBack) return;
    const target = done ? total - 1 : current - 1;
    if (done) setDone(false);
    setCurrent(target);
    setRevealed(!!results[target]);
  };

  // Swipe handlers (only active after answer is revealed)
  // Swipe handlers are attached natively with { passive: false }: React attaches
  // touchmove passively at the root, so preventDefault() from a JSX onTouchMove is
  // ignored and the browser keeps the gesture (page pan / overscroll) instead.
  const EDGE_DEAD_ZONE = 28; // leave iOS Safari's back-swipe strip alone

  // Latest state for the native listeners, so they can be bound once and never
  // rebind mid-gesture (a rebind can make later touchmove events non-cancelable).
  const liveRef = useRef({ revealed, done, reviewMode, handleMark, toggleFlag });
  liveRef.current = { revealed, done, reviewMode, handleMark, toggleFlag };

  // Bound on document, not the card: a swipe that starts on blank space around
  // or below the card must count too.
  useEffect(() => {

    const onStart = (e) => {
      // Gestures that begin on a control, the context line, the action bar, or
      // the sheet are theirs, not the card's.
      const el = e.target;
      if (el && el.closest && el.closest("button, a, input, textarea, select, label, .q-topline, .q-actionbar, .q-sheet, .q-sheet-backdrop")) return;
      const t = e.touches[0];
      const fromEdge = t.clientX < EDGE_DEAD_ZONE || t.clientX > window.innerWidth - EDGE_DEAD_ZONE;
      touchRef.current = { startX: t.clientX, startY: t.clientY, locked: fromEdge, horizontal: false, samples: [{ x: t.clientX, t: Date.now() }], ySamples: [{ y: t.clientY, t: Date.now() }] };
      setSwiping(false);
      setSwipeX(0);
    };

    const onMove = (e) => {
      const { revealed: isRevealed, done: isDone, reviewMode: inReview } = liveRef.current;
      if (isDone || inReview) return;
      const ref = touchRef.current;
      if (!ref) return;
      const t = e.touches[0];
      const dx = t.clientX - ref.startX;
      const dy = t.clientY - ref.startY;
      if (!ref.locked) {
        if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
        ref.locked = true;
        ref.horizontal = Math.abs(dx) > Math.abs(dy) * 1.25;
      }
      ref.dy = dy;
      ref.ySamples.push({ y: t.clientY, t: Date.now() });
      if (ref.ySamples.length > 12) ref.ySamples.shift();
      if (!ref.horizontal) {
        // Upward swipe flags when the page can't scroll any further down.
        // Works before or after the reveal. Mid-scroll, an upward swipe keeps
        // scrolling (the browser owns it).
        if (dy < 0) {
          const atBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 8;
          if (atBottom) {
            if (e.cancelable) e.preventDefault();
            ref.flagCandidate = true;
          }
        }
        return;
      }
      if (!isRevealed) return; // horizontal got-it/missed swipes need the answer shown
      if (e.cancelable) e.preventDefault();
      ref.dx = dx;
      ref.samples.push({ x: t.clientX, t: Date.now() });
      if (ref.samples.length > 12) ref.samples.shift();
      setSwiping(true);
      setSwipeX(dx);
    };

    const onEnd = () => {
      const ref = touchRef.current;
      touchRef.current = null;
      const { revealed: isRevealed, done: isDone, reviewMode: inReview, handleMark: mark } = liveRef.current;
      if (!ref) {
        setSwipeX(0);
        setSwiping(false);
        return;
      }
      // Upward flick = flag/unflag the current question. A slow drag just
      // scrolls (we never preventDefault for vertical), so only a fast flick
      // triggers the flag. Works before or after the reveal.
      if (!ref.horizontal) {
        const ys = ref.ySamples || [];
        let velY = 0;
        if (ys.length > 1) {
          const lastY = ys[ys.length - 1];
          let baseY = ys[0];
          for (let i = ys.length - 1; i >= 0; i--) {
            if (ys[i].t <= lastY.t - 120) { baseY = ys[i]; break; }
          }
          const dtY = lastY.t - baseY.t;
          if (dtY > 0) velY = (lastY.y - baseY.y) / dtY;
        }
        const dyTotal = ref.dy || 0;
        if (!isDone && !inReview && ref.flagCandidate && (dyTotal <= -36 || velY <= -0.35)) {
          liveRef.current.toggleFlag();
        }
        setSwipeX(0);
        setSwiping(false);
        return;
      }
      if (!isRevealed || isDone || inReview) {
        setSwipeX(0);
        setSwiping(false);
        return;
      }
      const dx = ref.dx || 0;
      // Velocity over the last ~120ms: a short fast flick counts as a swipe.
      let vel = 0;
      const sm = ref.samples;
      if (sm && sm.length > 1) {
        const last = sm[sm.length - 1];
        let base = sm[0];
        for (let i = sm.length - 1; i >= 0; i--) {
          if (sm[i].t <= last.t - 120) { base = sm[i]; break; }
        }
        const dt = last.t - base.t;
        if (dt > 0) vel = (last.x - base.x) / dt;
      }
      setSwipeX(0);
      setSwiping(false);
      const flick = Math.abs(dx) >= FLICK_MIN_DIST && Math.abs(vel) >= FLICK_MIN_VEL && Math.sign(vel) === Math.sign(dx);
      if (dx > SWIPE_THRESHOLD || (flick && dx > 0)) mark(true);
      else if (dx < -SWIPE_THRESHOLD || (flick && dx < 0)) mark(false);
    };

    document.addEventListener("touchstart", onStart, { passive: true });
    document.addEventListener("touchmove", onMove, { passive: false });
    document.addEventListener("touchend", onEnd, { passive: true });
    document.addEventListener("touchcancel", onEnd, { passive: true });
    return () => {
      document.removeEventListener("touchstart", onStart);
      document.removeEventListener("touchmove", onMove);
      document.removeEventListener("touchend", onEnd);
      document.removeEventListener("touchcancel", onEnd);
    };
  }, []);

  // Tap anywhere on the study screen to reveal the answer.
  // Bound on document so blank space around the card counts too. Guards: only
  // before the reveal, never while the sheet is open, never on a control, never
  // when the tap was really the end of a drag or a text selection.
  const tapRef = useRef({ moved: false });
  useEffect(() => {
    if (reviewMode || done) return;

    const onTouchStart = (e) => {
      const t = e.touches[0];
      tapRef.current = { moved: false, x: t.clientX, y: t.clientY };
    };
    const onTouchMove = (e) => {
      const r = tapRef.current;
      if (!r || r.moved) return;
      const t = e.touches[0];
      if (Math.abs(t.clientX - r.x) > 10 || Math.abs(t.clientY - r.y) > 10) r.moved = true;
    };
    const onClick = (e) => {
      if (revealed || done || sheetOpen || reviewMode) return;
      if (tapRef.current && tapRef.current.moved) return;
      const el = e.target;
      if (el && el.closest && el.closest("button, a, input, textarea, select, label, .q-sheet, .q-sheet-backdrop")) return;
      const sel = window.getSelection && window.getSelection();
      if (sel && String(sel).length > 0) return;
      setRevealed(true);
    };

    document.addEventListener("touchstart", onTouchStart, { passive: true });
    document.addEventListener("touchmove", onTouchMove, { passive: true });
    document.addEventListener("click", onClick);
    return () => {
      document.removeEventListener("touchstart", onTouchStart);
      document.removeEventListener("touchmove", onTouchMove);
      document.removeEventListener("click", onClick);
    };
  }, [revealed, done, sheetOpen, reviewMode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if (reviewMode) return;
      if (e.key === "f" && !done) { toggleFlag(); return; }
      if ((e.key === "b" || e.key === "p") && canBack) { handleBack(); return; }
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
  }, [revealed, done, current, total, reviewMode, canBack, results]);

  const openSheet = () => {
    setSheetBank(null);
    setCatQuery("");
    setSheetOpen(true);
  };

  const closeSheet = () => {
    setSheetOpen(false);
    setSheetBank(null);
    setCatQuery("");
  };

  const chooseCategory = (targetBank, cat) => {
    closeSheet();
    if (targetBank === bank) {
      if (cat !== category || done) startNew(cat, bank);
      return;
    }
    pendingRef.current = { bank: targetBank, category: cat };
    setBank(targetBank);
  };

  const sheet = !sheetOpen ? null : (
    <div className="q-sheet-backdrop" onClick={closeSheet}>
      <div className="q-sheet" onClick={(e) => e.stopPropagation()}>
        <div className="q-sheet-grip" />
        <div className="q-sheet-head">
          {sheetBank ? (
            <button className="q-sheet-back" onClick={() => { setSheetBank(null); setCatQuery(""); }}>
              Banks
            </button>
          ) : (
            <span className="q-sheet-title">Question banks</span>
          )}
          {sheetBank && <span className="q-sheet-title">{BANKS[sheetBank].label}</span>}
          <button className="q-sheet-close" onClick={closeSheet} aria-label="Close">Done</button>
        </div>

        {!sheetBank ? (
          <div className="q-sheet-list">
            {(() => {
              const missedAll = collectMissed();
              return (
                <button
                  className={`q-sheet-row q-sheet-row-missed ${bank === MISSED_BANK ? "q-sheet-row-active" : ""}`}
                  disabled={missedAll.length === 0}
                  onClick={() => missedAll.length > 0 && chooseCategory(MISSED_BANK, "All")}
                >
                  <span className="q-sheet-row-main">
                    <span className="q-sheet-row-title">Review missed</span>
                    <span className="q-sheet-row-sub">
                      {missedAll.length === 0
                        ? "Nothing missed yet"
                        : `${missedAll.length} question${missedAll.length === 1 ? "" : "s"} across all banks`}
                    </span>
                  </span>
                  {missedAll.length > 0 && <span className="q-sheet-chev">›</span>}
                </button>
              );
            })()}
            {(() => {
              const flaggedAll = collectFlagged();
              return (
                <button
                  className={`q-sheet-row q-sheet-row-flagged ${bank === FLAG_BANK ? "q-sheet-row-active" : ""}`}
                  disabled={flaggedAll.length === 0}
                  onClick={() => flaggedAll.length > 0 && chooseCategory(FLAG_BANK, "All")}
                >
                  <span className="q-sheet-row-main">
                    <span className="q-sheet-row-title">Review flagged</span>
                    <span className="q-sheet-row-sub">
                      {flaggedAll.length === 0
                        ? "Swipe up on any question to flag it"
                        : `${flaggedAll.length} question${flaggedAll.length === 1 ? "" : "s"} across all banks`}
                    </span>
                  </span>
                  {flaggedAll.length > 0 && <span className="q-sheet-chev">›</span>}
                </button>
              );
            })()}
            {Object.entries(BANKS).map(([key, val]) => {
              const p = bankProgress(key);
              return (
                <button key={key} className={`q-sheet-row ${key === bank ? "q-sheet-row-active" : ""}`} onClick={() => setSheetBank(key)}>
                  <span className="q-sheet-row-main">
                    <span className="q-sheet-row-title">{val.label}</span>
                    <span className="q-sheet-row-sub">
                      {val.questions.length} questions
                      {p.seen > 0 && ` · ${p.seen} done, ${Math.round((p.correct / p.seen) * 100)}% got it`}
                      {key === bank && p.category !== "All" && ` · ${p.category}`}
                    </span>
                  </span>
                  <span className="q-sheet-chev">›</span>
                </button>
              );
            })}
          </div>
        ) : (
          <>
            {getCategoryCounts(sheetBank).length > 12 && (
              <div className="q-sheet-search">
                <input
                  type="text"
                  inputMode="search"
                  autoFocus={false}
                  className="q-sheet-input"
                  placeholder={`Search ${getCategoryCounts(sheetBank).length} categories`}
                  value={catQuery}
                  onChange={(e) => setCatQuery(e.target.value)}
                />
                {catQuery && (
                  <button className="q-sheet-clear" onClick={() => setCatQuery("")} aria-label="Clear">×</button>
                )}
              </div>
            )}
            <div className="q-sheet-list">
              {!catQuery && (
                <button
                  className={`q-sheet-row ${sheetBank === bank && category === "All" ? "q-sheet-row-active" : ""}`}
                  onClick={() => chooseCategory(sheetBank, "All")}
                >
                  <span className="q-sheet-row-main">
                    <span className="q-sheet-row-title">All categories</span>
                    <span className="q-sheet-row-sub">{BANKS[sheetBank].questions.length} questions</span>
                  </span>
                  {sheetBank === bank && category === "All" && <span className="q-sheet-check">✓</span>}
                </button>
              )}
              {getCategoryCounts(sheetBank)
                .filter((c) => c.name.toLowerCase().includes(catQuery.trim().toLowerCase()))
                .map((c) => {
                  const selected = sheetBank === bank && category === c.name;
                  return (
                    <button key={c.name} className={`q-sheet-row ${selected ? "q-sheet-row-active" : ""}`} onClick={() => chooseCategory(sheetBank, c.name)}>
                      <span className="q-sheet-row-main">
                        <span className="q-sheet-row-title">{c.name}</span>
                        <span className="q-sheet-row-sub">{c.count} question{c.count === 1 ? "" : "s"}</span>
                      </span>
                      {selected && <span className="q-sheet-check">✓</span>}
                    </button>
                  );
                })}
            </div>
          </>
        )}
      </div>
    </div>
  );

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
                {item.img && <img className="q-review-img" src={item.img} alt={item.alt || ""} loading="lazy" />}
                {isOpen && (
                  <div className="q-answer-block">
                    <div className="q-divider-line" />
                    <AnswerText text={item.a} />
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
        {sheet}
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
          <button className="q-btn q-btn-secondary" onClick={handleBack} style={{ marginTop: 8 }}>
            ‹ Back to last card
          </button>
          <button className="q-btn q-btn-primary" onClick={() => startNew(category)} style={{ marginTop: 8 }}>
            Restart {category === "All" ? "All" : category}
          </button>
          <button className="q-btn q-btn-secondary" onClick={openSheet} style={{ marginTop: 8 }}>
            Pick bank or category
          </button>
        </div>
        {sheet}
      </div>
    );
  }

  if (!q) return null;

  return (
    <div className="q-container">
      {/* One control: what you are studying, tap to change */}
      <div className="q-topline">
        <button className="q-context" onClick={openSheet}>
          <span className="q-context-bank">{bankLabel(bank)}</span>
          {bank === MISSED_BANK || bank === FLAG_BANK ? (
            <span className="q-context-cat">all banks</span>
          ) : (
            <span className="q-context-cat">{category === "All" ? "All" : category}</span>
          )}
          <span className="q-context-chev">▾</span>
        </button>
        <div className="q-topline-meta">
          {missed.length > 0 && (
            <button className="q-missed-btn" onClick={() => setReviewMode(true)}>{missed.length} missed</button>
          )}
          <span className="q-counter">{current + 1}/{total}</span>
          <span className="q-green">{score.correct}</span>
          <span className="q-divider">/</span>
          <span className="q-red">{score.wrong}</span>
        </div>
      </div>

      <div className="q-progress-track">
        <div className="q-progress-fill" style={{ width: `${pct}%` }} />
      </div>

      {/* Card */}
      <div
        className={`q-card ${swiping && swipeX > SWIPE_THRESHOLD ? "q-card-right" : ""} ${swiping && swipeX < -SWIPE_THRESHOLD ? "q-card-left" : ""}`}
        onClick={() => !revealed && !swiping && setRevealed(true)}
        style={swiping ? { transform: `translateX(${swipeX * 0.4}px) rotate(${swipeX * 0.02}deg)`, transition: "none" } : {}}
      >
        {q.id && (
          <button
            className={`q-flag-badge ${flags.has(q.id) ? "q-flag-badge-on" : ""}`}
            onClick={(e) => { e.stopPropagation(); toggleFlag(); }}
            aria-label={flags.has(q.id) ? "Unflag question" : "Flag question"}
          >{flags.has(q.id) ? "🚩" : "⚐"}</button>
        )}
        {flagFlash && <div className="q-flag-flash">{flagFlash}</div>}
        {swiping && Math.abs(swipeX) > SWIPE_THRESHOLD && (
          <div className={`q-swipe-label ${swipeX > 0 ? "q-swipe-right" : "q-swipe-left"}`}>
            {swipeX > 0 ? "Got it" : "Missed"}
          </div>
        )}
        <div className="q-question">{q.q}</div>

        {q.img && <img className="q-question-img" src={q.img} alt={q.alt || ""} loading="lazy" />}

        {revealed && (
          <div className="q-answer-block">
            <div className="q-divider-line" />
            <AnswerText text={q.a} />
          </div>
        )}
      </div>

      {/* Bottom action bar, always under the thumb */}
      <div className="q-actionbar">
        {revealed ? (
          (() => {
            const marked = results[current];
            return (
              <div className="q-actions">
                <button
                  className="q-btn q-btn-back"
                  onClick={handleBack}
                  disabled={!canBack}
                  aria-label="Previous card"
                >‹</button>
                <button className={`q-btn q-btn-miss ${marked === "wrong" ? "q-btn-chosen" : ""}`} onClick={() => handleMark(false)}>Missed it</button>
                <button className={`q-btn q-btn-got ${marked === "correct" ? "q-btn-chosen" : ""}`} onClick={() => handleMark(true)}>Got it</button>
              </div>
            );
          })()
        ) : (
          <div className="q-reveal-row">
            <button
              className="q-btn q-btn-back"
              onClick={handleBack}
              disabled={!canBack}
              aria-label="Previous card"
            >‹</button>
            <button className="q-btn q-btn-reveal" onClick={() => setRevealed(true)}>Show answer</button>
          </div>
        )}
      </div>

      {sheet}
    </div>
  );

}
