import { useEffect, useState } from "react";
import { Analytics } from "@vercel/analytics/react";


import { BANKS } from "./data/banks";
import Questions from "./components/Questions";
import RotationPdfs from "./components/RotationPdfs";

import "./App.css";

export default function App() {
  const [hash, setHash] = useState(window.location.hash);
  useEffect(() => {
    const onChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const step = hash === "#shelves" ? "shelves" : "step2";
  const selectStep = (nextStep) => { window.location.hash = nextStep; };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1 className="header-title-link" style={{ cursor: "pointer" }}>ValidMed</h1>
            <p className="tagline">Shelf exams + Step 2 CK</p>
          </div>
        </div>
        <nav className="step-selector" aria-label="Study view">
          <button type="button" aria-pressed={step === "shelves"} onClick={() => selectStep("shelves")}>Shelf exams</button>
          <button type="button" aria-pressed={step === "step2"} onClick={() => selectStep("step2")}>Step 2 CK</button>
        </nav>
      </header>

      <main className="app-main">
        {hash === "#practice" ? <><div className="practice-heading"><a href="#step2">‹ Back to resources</a><p>FM: {BANKS.s2fm.questions.length} cards. {BANKS.s2fm.coverage}</p></div><Questions /></> : <RotationPdfs view={step} />}
      </main>

      <Analytics />
    </div>
  );
}
