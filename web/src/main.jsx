import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { bootstrapSync } from "./sync";
import { migrateImmunoIds } from "./migrate";
import "./index.css";

bootstrapSync()
  .catch(() => {})
  .then(() => {
    try {
      migrateImmunoIds();
    } catch {}
  })
  .finally(() => {
    ReactDOM.createRoot(document.getElementById("root")).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });
