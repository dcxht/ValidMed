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
  const resources = hash === "#resources";
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div><h1>ValidMed</h1><p className="tagline">Shelf exams + Step 2 CK</p></div>
          <a className="resources-nav" href={resources ? "#practice" : "#resources"}>{resources ? "Practice" : "Resources"}</a>
        </div>
      </header>
      <main className="app-main">
        {resources ? <RotationPdfs /> : <>
          <div className="practice-heading">
            <p>{BANKS.s2fm.questions.length} FM cards · Selected points, pp. 4-28 / 319. Full coverage in progress.</p>
          </div>
          <Questions />
        </>}
      </main>
      <Analytics />
    </div>
  );
}
