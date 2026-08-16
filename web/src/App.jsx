import { Analytics } from "@vercel/analytics/react";
import Questions from "./components/Questions";
import "./App.css";

export default function App() {
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
        <Questions />
      </main>

      <Analytics />
    </div>
  );
}
