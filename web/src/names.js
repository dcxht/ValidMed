// Personal quiz copies: each name gets /<name> - the full quiz, identical to
// the homepage, with its own on-device memory (marks, flags, history).
// To add another person, add one entry here.
export const NAMES = ["c", "jai", "quoc", "naser"];

const seg = window.location.pathname.replace(/^\/+|\/+$/g, "");
export const PERSON = NAMES.includes(seg) ? seg : null;

// Storage namespace: public homepage keeps the original keys; personal copies
// get "<name>_" prefixed keys so each person's memory stays separate.
export function key(base) {
  return PERSON ? `${PERSON}_${base}` : base;
}

// First visit to a personal copy: import whatever memory the public homepage
// already had on this device (progress, flags, history), so "my own page"
// starts from where that person actually was. Copy-if-absent per key, so
// later homepage use never overwrites the personal copy's own progress.
if (PERSON) {
  try {
    const prefix = `${PERSON}_`;
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith("validmed_") && !localStorage.getItem(prefix + k)) {
        localStorage.setItem(prefix + k, localStorage.getItem(k));
      }
    }
  } catch {}
}
