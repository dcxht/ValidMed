import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { bootstrapSync } from "./sync";
import "./index.css";

bootstrapSync().finally(() => {
  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});
