import { useState } from "react";
import { Analytics } from "@vercel/analytics/react";
import DeviceTable from "./components/DeviceTable";
import DeviceDetail from "./components/DeviceDetail";
import Methodology from "./components/Methodology";
import Questions from "./components/Questions";
import "./App.css";

export default function App() {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [view, setView] = useState("questions"); // "devices" | "methodology" | "questions"

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-row">
          <div>
            <h1 className="header-title-link">QBank</h1>
            <p className="tagline">NBME-style clinical vignettes</p>
          </div>
          {/* nav hidden for now */}
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
