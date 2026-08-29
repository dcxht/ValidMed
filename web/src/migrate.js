// One-time id migration: the immunology bank's question ids used to be
// "im1".."im203", which collided with the NBME Images bank ("im1".."im155")
// in the global id map - any saved immuno card with id <= 155 hydrated to an
// NBME Images card. Immuno ids are now "imm<N>". This rewrites saved
// on-device state (sessions, missed/flagged queues, flags, history) so
// existing progress survives the rename. Runs on every boot and is a no-op
// once nothing matches the old pattern.
const OLD_RE = /^im(\d+)$/;

function mapId(id) {
  const m = OLD_RE.exec(id);
  return m ? `imm${m[1]}` : id;
}

// Rewrite ids on question objects in a saved session. immunoOnly=false is for
// the cross-bank missed/flagged queues, where an object may come from either
// bank: every NBME Images card's category starts with "NBME", no immuno
// category does (a few immuno cards have images, so `img` cannot separate
// them).
function migrateSession(raw, immunoOnly) {
  try {
    const st = JSON.parse(raw);
    if (!st || !Array.isArray(st.queue)) return raw;
    let changed = false;
    const fix = (q) => {
      if (q && OLD_RE.test(q.id) && (immunoOnly || !/^NBME/.test(q.category || ""))) {
        q.id = mapId(q.id);
        changed = true;
      }
      return q;
    };
    st.queue = st.queue.map(fix);
    if (Array.isArray(st.missed)) st.missed = st.missed.map(fix);
    return changed ? JSON.stringify(st) : raw;
  } catch {
    return raw;
  }
}

function loadHist(prefix) {
  try {
    const raw = localStorage.getItem(prefix + "validmed_history");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

// Flags are a flat id list shared across banks, so "imN" with N <= 155 is
// ambiguous. N > 155 can only be immuno. For N <= 155, attribute from the
// most recent flag event for that id in history; with no event, leave it
// pointing at NBME Images (the bank those ids have hydrated to since launch).
function migrateFlags(raw, hist) {
  try {
    const ids = JSON.parse(raw);
    if (!Array.isArray(ids)) return raw;
    let changed = false;
    const out = ids.map((id) => {
      const m = OLD_RE.exec(id);
      if (!m) return id;
      const n = parseInt(m[1], 10);
      let immuno = n > 155;
      if (!immuno) {
        const migrated = `imm${m[1]}`;
        for (let i = hist.length - 1; i >= 0; i--) {
          const ev = hist[i];
          if (ev && ev.type === "flag" && (ev.id === id || ev.id === migrated)) {
            immuno = ev.bank === "immuno";
            break;
          }
        }
      }
      if (immuno) {
        changed = true;
        return `imm${m[1]}`;
      }
      return id;
    });
    return changed ? JSON.stringify(out) : raw;
  } catch {
    return raw;
  }
}

function migrateHistory(raw) {
  try {
    const list = JSON.parse(raw);
    if (!Array.isArray(list)) return raw;
    let changed = false;
    const out = list.map((ev) => {
      if (ev && ev.bank === "immuno" && OLD_RE.test(ev.id)) {
        changed = true;
        return { ...ev, id: mapId(ev.id) };
      }
      return ev;
    });
    return changed ? JSON.stringify(out) : raw;
  } catch {
    return raw;
  }
}

export function migrateImmunoIds() {
  const SUFFIXES = ["validmed_q_immuno", "validmed_q___missed__", "validmed_q___flagged__", "validmed_flags", "validmed_history"];
  const jobs = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (!k) continue;
    for (const sfx of SUFFIXES) {
      if (k === sfx || k.endsWith("_" + sfx)) {
        const prefix = k.slice(0, k.length - sfx.length);
        jobs.push({ k, sfx, prefix });
        break;
      }
    }
  }
  // Flags read history for bank attribution, so history must migrate last.
  jobs.sort((a, b) => (a.sfx === "validmed_history") - (b.sfx === "validmed_history"));
  for (const { k, sfx, prefix } of jobs) {
    const raw = localStorage.getItem(k);
    if (raw == null) continue;
    let next = raw;
    if (sfx === "validmed_q_immuno") next = migrateSession(raw, true);
    else if (sfx === "validmed_q___missed__" || sfx === "validmed_q___flagged__") next = migrateSession(raw, false);
    else if (sfx === "validmed_flags") next = migrateFlags(raw, loadHist(prefix));
    else if (sfx === "validmed_history") next = migrateHistory(raw);
    if (next !== raw) localStorage.setItem(k, next);
  }
}
