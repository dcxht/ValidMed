import { useState } from "react";
import { Analytics } from "@vercel/analytics/react";
import DeviceTable from "./components/DeviceTable";
import DeviceDetail from "./components/DeviceDetail";
import Methodology from "./components/Methodology";
import Questions from "./components/Questions";
import "./App.css";

export default function App() {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [view, setView] = useState("devices"); // "devices" | "methodology" | "questions"

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1 className="header-title-link" onClick={() => { setView("devices"); setSelectedDevice(null); }} style={{ cursor: "pointer" }}>ValidMed</h1>
            <p className="tagline">FDA AI/ML device evidence tracker</p>
          </div>
          <nav className="header-nav">
            <button className={`nav-btn ${view === "devices" ? "nav-btn-active" : ""}`} onClick={() => { setView("devices"); setSelectedDevice(null); }}>Database</button>
            <button className={`nav-btn ${view === "methodology" ? "nav-btn-active" : ""}`} onClick={() => setView("methodology")}>Methodology</button>
            <button className={`nav-btn ${view === "questions" ? "nav-btn-active" : ""}`} onClick={() => setView("questions")}>QBank</button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {view === "questions" ? (
          <Questions />
        ) : view === "methodology" ? (
          <Methodology onBack={() => setView("devices")} />
        ) : selectedDevice ? (
          <DeviceDetail
            deviceId={selectedDevice}
            onBack={() => setSelectedDevice(null)}
          />
        ) : (
          <DeviceTable onSelectDevice={setSelectedDevice} />
        )}
      </main>

      {/* footer hidden for now */}
      <Analytics />
    </div>
  );
}
