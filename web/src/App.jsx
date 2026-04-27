import { useState } from "react";
import DeviceTable from "./components/DeviceTable";
import DeviceDetail from "./components/DeviceDetail";
import Methodology from "./components/Methodology";
import "./App.css";

export default function App() {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [view, setView] = useState("devices"); // "devices" | "methodology"

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1
              className="header-title-link"
              onClick={() => { setView("devices"); setSelectedDevice(null); }}
            >
              ValidMed
            </h1>
            <p className="tagline">
              Verified AI Literature & Intelligence Database for Medical Devices
            </p>
          </div>
          <nav className="header-nav">
            <button
              className={`nav-btn ${view === "devices" ? "nav-btn-active" : ""}`}
              onClick={() => { setView("devices"); setSelectedDevice(null); }}
            >
              Devices
            </button>
            <button
              className={`nav-btn ${view === "methodology" ? "nav-btn-active" : ""}`}
              onClick={() => setView("methodology")}
            >
              Methodology
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {view === "methodology" ? (
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

      <footer className="app-footer">
        <p>
          ValidMed — Verified AI Literature & Intelligence Database for Medical Devices.
          Data sourced from FDA, PubMed, OpenAlex, MAUDE, and ClinicalTrials.gov.
          Open source. Not affiliated with the FDA. <a href="https://github.com/dcxht/ValidMed" target="_blank" rel="noopener noreferrer" style={{color: 'var(--accent)'}}>GitHub</a>
        </p>
      </footer>
    </div>
  );
}
