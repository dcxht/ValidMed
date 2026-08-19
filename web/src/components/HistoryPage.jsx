import { useMemo } from "react";
import { BANKS } from "../data/banks";
import { loadHistory } from "../historyStore";
import { key } from "../names";

function bankOf(id) {
  for (const [k, b] of Object.entries(BANKS)) {
    if (b.questions.some((q) => q.id === id)) return k;
  }
  return null;
}

function findQuestion(id) {
  const bk = bankOf(id);
  if (!bk) return null;
  return { bank: bk, q: BANKS[bk].questions.find((q) => q.id === id) };
}

export default function HistoryPage() {
  const events = useMemo(() => loadHistory(), []);
  const marks = events.filter((e) => e.type === "mark");
  const perBank = {};
  for (const m of marks) {
    const bk = m.bank || bankOf(m.id) || "?";
    perBank[bk] = perBank[bk] || { n: 0, c: 0, last: 0 };
    perBank[bk].n += 1;
    if (m.correct) perBank[bk].c += 1;
    if (m.ts > perBank[bk].last) perBank[bk].last = m.ts;
  }
  let flags = [];
  try {
    flags = JSON.parse(localStorage.getItem(key("validmed_flags")) || "[]");
  } catch {}
  const recent = [...events].reverse().slice(0, 50);

  return (
    <div className="hist-wrap">
      <h2>History</h2>
      <h3>Per bank</h3>
      {Object.keys(perBank).length === 0 && <p className="gate-sub">No questions marked yet.</p>}
      <div className="hist-banks">
        {Object.entries(perBank).map(([bk, s]) => (
          <div key={bk} className="hist-bank-row">
            <span className="hist-bank-name">{BANKS[bk] ? BANKS[bk].label : bk}</span>
            <span>{s.n} marked</span>
            <span>{s.n ? Math.round((100 * s.c) / s.n) : 0}% correct</span>
          </div>
        ))}
      </div>
      <h3>Flagged ({flags.length})</h3>
      {flags.map((id) => {
        const hit = findQuestion(id);
        return (
          <div key={id} className="hist-flag-row">
            <span className="hist-bank-name">{hit ? BANKS[hit.bank].label : "?"}</span>
            <span className="hist-q">{hit ? hit.q.q.slice(0, 90) : id}</span>
          </div>
        );
      })}
      <h3>Recent</h3>
      {recent.map((e, i) => (
        <div key={i} className="hist-event-row">
          <span className="hist-ts">{new Date(e.ts).toLocaleString()}</span>
          <span>
            {e.type === "mark" ? (e.correct ? "Got it" : "Missed") : e.flagged ? "Flagged" : "Unflagged"} {e.id}
          </span>
        </div>
      ))}
      {events.length === 0 && <p className="gate-sub">Nothing recorded yet. History starts with your next mark or flag.</p>}
    </div>
  );
}
