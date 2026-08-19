import { useEffect, useState } from "react";
import { Analytics } from "@vercel/analytics/react";
import Questions from "./components/Questions";
import HistoryPage from "./components/HistoryPage";
import "./App.css";

export default function App() {
  const [hash, setHash] = useState(window.location.hash);
  useEffect(() => {
    const onChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

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
        {hash === "#history" ? <HistoryPage /> : <Questions />}
      </main>

      <Analytics />
    </div>
  );
}
