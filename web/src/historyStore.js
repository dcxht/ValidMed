// On-device quiz history + passcode gate. Nothing leaves the browser:
// the passcode is only ever stored as a salted SHA-256 hash in localStorage,
// and history events stay on the device they were recorded on.
const HIST_KEY = "validmed_history";
const GATE_KEY = "validmed_gate";
const MAX_EVENTS = 2000;

export function recordEvent(ev) {
  try {
    const raw = localStorage.getItem(HIST_KEY);
    const list = raw ? JSON.parse(raw) : [];
    list.push({ ...ev, ts: Date.now() });
    if (list.length > MAX_EVENTS) list.splice(0, list.length - MAX_EVENTS);
    localStorage.setItem(HIST_KEY, JSON.stringify(list));
  } catch {}
}

export function loadHistory() {
  try {
    const raw = localStorage.getItem(HIST_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return [];
}

async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function hasGate() {
  try {
    return !!localStorage.getItem(GATE_KEY);
  } catch {
    return false;
  }
}

export async function setGate(pass) {
  const salt = [...crypto.getRandomValues(new Uint8Array(16))].map((b) => b.toString(16).padStart(2, "0")).join("");
  const hash = await sha256Hex(salt + ":" + pass);
  localStorage.setItem(GATE_KEY, JSON.stringify({ salt, hash }));
}

export async function checkGate(pass) {
  try {
    const raw = localStorage.getItem(GATE_KEY);
    if (!raw) return false;
    const { salt, hash } = JSON.parse(raw);
    return (await sha256Hex(salt + ":" + pass)) === hash;
  } catch {
    return false;
  }
}
