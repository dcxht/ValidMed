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
