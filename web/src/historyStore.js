// On-device quiz history. Personal copies (/Chetd, /jai, ...) each get their
// own key via names.js, so every person's history stays separate on the device.
import { key } from "./names";

const HIST_BASE = "validmed_history";
const MAX_EVENTS = 2000;

export function recordEvent(ev) {
  try {
    const k = key(HIST_BASE);
    const raw = localStorage.getItem(k);
    const list = raw ? JSON.parse(raw) : [];
    list.push({ ...ev, ts: Date.now() });
    if (list.length > MAX_EVENTS) list.splice(0, list.length - MAX_EVENTS);
    localStorage.setItem(k, JSON.stringify(list));
  } catch {}
}

export function loadHistory() {
  try {
    const raw = localStorage.getItem(key(HIST_BASE));
    if (raw) return JSON.parse(raw);
  } catch {}
  return [];
}
