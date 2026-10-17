import fs from "fs";
const terse = JSON.parse(fs.readFileSync("/tmp/vmfix/terse.json","utf8"));

// Vignette cue: age/sex tokens or patient nouns -> already a real exam question
const VIG = /\b\d{1,2}\s?[- ]?(?:M|F|M\/F|yo|y\/o|year-old|month-old|week-old|day-old)\b|\b(?:Boy|Girl|Infant|Neonate|Newborn|Child|Kid|Baby|Toddler|Teen|Man|Woman|Patient|G3P|G\dP\d|male|female|woman|man|mother|gravid)\b/i;

// Tier A templates: safe prefix conversions
function tierA(f) {
  let m;
  const base = f.replace(/\?+$/,"").trim();
  if ((m = base.match(/^most common (.+)/i))) return `What is the most common ${m[1]}?`;
  if ((m = base.match(/^best (.+)/i))) return `What is the best ${m[1]}?`;
  if ((m = base.match(/^first[- ]line (.+)/i))) return `What is the first-line ${m[1]}?`;
  if ((m = base.match(/^treatment (?:of|for) (.+)/i))) return `What is the treatment for ${m[1]}?`;
  if ((m = base.match(/^treatment of (.+) versus (.+)/i))) return null; // keep for hand
  if ((m = base.match(/^mechanism of (.+)/i))) return `What is the mechanism of ${m[1]}?`;
  if ((m = base.match(/^causes? of (.+)/i))) return `What are the causes of ${m[1]}?`;
  if ((m = base.match(/^diagnosis of (.+)/i))) return `How is ${m[1]} diagnosed?`;
  if ((m = base.match(/^management of (.+)/i))) return `How is ${m[1]} managed?`;
  if ((m = base.match(/^risk factors? (?:of|for) (.+)/i))) return `What are the risk factors for ${m[1]}?`;
  if ((m = base.match(/^side effects? of (.+)/i))) return `What are the side effects of ${m[1]}?`;
  if ((m = base.match(/^complications? of (.+)/i))) return `What are the complications of ${m[1]}?`;
  if ((m = base.match(/^definition of (.+)/i))) return `What is the definition of ${m[1]}?`;
  if ((m = base.match(/^etiology of (.+)/i))) return `What is the etiology of ${m[1]}?`;
  if ((m = base.match(/^drugs? causing (.+)/i))) return `Which drugs cause ${m[1]}?`;
  if ((m = base.match(/^drugs? (?:for|used (?:for|in|to treat)) (.+)/i))) return `Which drugs are used for ${m[1]}?`;
  return null;
}

const vignette = [], tierAout = [], hand = [];
for (const t of terse) {
  const f = t.front;
  if (VIG.test(f) && f.includes("?")) { vignette.push(t); continue; }
  const conv = tierA(f);
  if (conv) { tierAout.push({...t, converted: conv}); continue; }
  hand.push(t);
}
console.log("vignette (keep as-is):", vignette.length);
console.log("tier-A (template):", tierAout.length);
console.log("hand rewrite:", hand.length);
fs.writeFileSync("/tmp/vmfix/tierA.json", JSON.stringify(tierAout, null, 1));
fs.writeFileSync("/tmp/vmfix/vignette.json", JSON.stringify(vignette, null, 1));
fs.writeFileSync("/tmp/vmfix/hand.json", JSON.stringify(hand, null, 1));
// per bank for hand
const per = {}; for (const t of hand) for (const it of t.items) per[it.bank]=(per[it.bank]||0)+1;
console.log("hand instances per bank:", per);
