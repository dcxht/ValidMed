import { useEffect, useState } from "react";
import { Analytics } from "@vercel/analytics/react";
import Questions from "./components/Questions";
import HistoryPage from "./components/HistoryPage";
import { PERSON } from "./names";
import "./App.css";

export default function App() {
  const [hash, setHash] = useState(window.location.hash);
  useEffect(() => {
    const onChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const showHistory = PERSON && hash === "#history";

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1 className="header-title-link" style={{ cursor: "pointer" }}>ValidMed</h1>
            <p className="tagline">Step 1 QBank</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        {showHistory ? <HistoryPage /> : <Questions />}
      </main>

      <Analytics />
    </div>
  );
}
