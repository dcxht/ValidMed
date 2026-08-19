// Cloud sync for personal copies: on boot, pull the person's server-side state
// into localStorage (cloud wins per key); on every write, push the whole
// namespace up (debounced). Falls back silently to on-device-only if the
// store isn't connected or the network fails.
import { PERSON } from "./names";

const PREFIX = PERSON ? `${PERSON}_` : null;
const BASE_RE = /^validmed_/;

function gather() {
  const state = {};
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith(PREFIX) && BASE_RE.test(k.slice(PREFIX.length))) {
        state[k.slice(PREFIX.length)] = localStorage.getItem(k);
      }
    }
  } catch {}
  return state;
}

export async function bootstrapSync() {
  if (!PERSON) return;
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 3500);
    const r = await fetch(`/api/sync?name=${encodeURIComponent(PERSON)}`, { signal: ctrl.signal });
    clearTimeout(t);
    if (!r.ok) return;
    const { state } = await r.json();
    if (state && typeof state === "object") {
      // Cloud is the mirror: local keys missing from cloud are dropped, so a
      // server-side reset (empty object) clears the device on next open.
      const drop = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(PREFIX)) {
          const base = k.slice(PREFIX.length);
          if (BASE_RE.test(base) && !(base in state)) drop.push(k);
        }
      }
      for (const k of drop) localStorage.removeItem(k);
      for (const [base, val] of Object.entries(state)) {
        if (BASE_RE.test(base) && typeof val === "string") {
          localStorage.setItem(PREFIX + base, val);
        }
      }
    }
  } catch {}
}

let timer = null;
function push() {
  if (!PERSON) return;
  const state = gather();
  fetch(`/api/sync?name=${encodeURIComponent(PERSON)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state }),
  }).catch(() => {});
}

export function schedulePush() {
  if (!PERSON) return;
  clearTimeout(timer);
  timer = setTimeout(push, 800);
}

// Any write to this person's namespace triggers a debounced push.
if (PERSON) {
  const orig = Storage.prototype.setItem;
  Storage.prototype.setItem = function (k, v) {
    orig.call(this, k, v);
    try {
      if (typeof k === "string" && k.startsWith(PREFIX) && BASE_RE.test(k.slice(PREFIX.length))) schedulePush();
    } catch {}
  };
}
