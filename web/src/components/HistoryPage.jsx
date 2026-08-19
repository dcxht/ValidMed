import { useMemo, useState } from "react";
import { BANKS } from "../data/banks";
import { hasGate, setGate, checkGate, loadHistory } from "../historyStore";
import Questions from "./Questions";

function bankOf(id) {
  for (const [key, b] of Object.entries(BANKS)) {
    if (b.questions.some((q) => q.id === id)) return key;
  }
  return null;
}

function findQuestion(id) {
  const bk = bankOf(id);
  if (!bk) return null;
  return { bank: bk, q: BANKS[bk].questions.find((q) => q.id === id) };
}

export default function HistoryPage() {
  const [gateReady] = useState(hasGate());
  const [unlocked, setUnlocked] = useState(false);
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!gateReady) {
      if (pass.length < 4) { setError("Pick at least 4 characters."); return; }
      if (pass !== pass2) { setError("Passcodes don't match."); return; }
      await setGate(pass);
      setUnlocked(true);
    } else {
      if (await checkGate(pass)) setUnlocked(true);
      else { setError("Wrong passcode."); setPass(""); }
    }
  };

  if (!unlocked) {
    return (
      <div className="gate-wrap">
        <h2>{gateReady ? "History" : "Set up History"}</h2>
        <p className="gate-sub">
          {gateReady ? "Enter your passcode." : "Choose a passcode. It never leaves this device."}
        </p>
        <form onSubmit={submit} className="gate-form">
          <input
            type="password"
            inputMode="text"
            autoComplete={gateReady ? "current-password" : "new-password"}
            placeholder="Passcode"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            autoFocus
          />
          {!gateReady && (
            <input
              type="password"
              inputMode="text"
              autoComplete="new-password"
              placeholder="Repeat passcode"
              value={pass2}
              onChange={(e) => setPass2(e.target.value)}
            />
          )}
          {error && <p className="gate-error">{error}</p>}
          <button type="submit" className="q-btn q-btn-reveal">{gateReady ? "Unlock" : "Save passcode"}</button>
        </form>
      </div>
    );
  }

  return <AuthedView />;
}

function AuthedView() {
  const [tab, setTab] = useState("quiz");
  return (
    <div>
      <div className="hist-tabs">
        <button className={tab === "quiz" ? "hist-tab hist-tab-active" : "hist-tab"} onClick={() => setTab("quiz")}>Quiz</button>
        <button className={tab === "history" ? "hist-tab hist-tab-active" : "hist-tab"} onClick={() => setTab("history")}>History</button>
      </div>
      {tab === "quiz" ? <Questions /> : <HistoryView />}
    </div>
  );
}

function HistoryView() {
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
    flags = JSON.parse(localStorage.getItem("validmed_flags") || "[]");
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
