import fs from "fs";
import { stripPageRefs } from "/tmp/vmfix/strip.mjs";
const banks = JSON.parse(fs.readFileSync("/tmp/vmfix/banks.json","utf8"));

const QW = /^(what|which|how|why|when|where|who|whose|whom|must|should|can|could|is|are|was|were|does|do|did|in |on |for |a |an |the |if |given |after |before |during |at |to |define|list|name|describe|identify|state|compare|distinguish|differentiate|walk through|which of|true or false)\b/i;
const isQ = q => QW.test(q)
  || /[:;.]\s*(what|which|how|why|when|where|who|must|should|can|could|is|are|does|do|did)\b/i.test(q)
  || /\b(what|which|how|why|must|should|does|do|is|are|can)\b[^?]*\?$/i.test(q)
  || /\.\s*(Diagnosis|Next|Next best step|Most likely|Treatment|Cause|Mechanism|Dx|Rx|Best next|Management|Organism|Triad|Defect|Finding|Syndrome)\??\.?\s*$/.test(q);

const fixed = {};   // bank -> [{card..., newQ}]
const terse = new Map(); // normQ -> {front, examples:[{bank,id,a,category}]}
let answerFixes = 0;
for (const [bank, cards] of Object.entries(banks)) {
  for (const c of cards) {
    const nq = stripPageRefs(c.q);
    const na = stripPageRefs(c.a);
    if (na !== c.a) answerFixes++;
    const rec = { bank, id: c.id, category: c.category, oldQ: c.q, newQ: nq, oldA: c.a, newA: na };
    (fixed[bank] ||= []).push(rec);
    if (!isQ(nq)) {
      const norm = nq.toLowerCase().replace(/[^a-z0-9]+/g," ").trim();
      if (!terse.has(norm)) terse.set(norm, { front: nq, items: [] });
      terse.get(norm).items.push({ bank, id: c.id, category: c.category, a: c.a });
    }
  }
}
console.log("answer backs cleaned:", answerFixes);
console.log("unique terse fronts:", terse.size);
let inst = 0; for (const v of terse.values()) inst += v.items.length;
console.log("terse card instances:", inst);
// per bank
const per = {};
for (const v of terse.values()) for (const it of v.items) per[it.bank]=(per[it.bank]||0)+1;
console.log(per);
fs.writeFileSync("/tmp/vmfix/fixed.json", JSON.stringify(fixed));
fs.writeFileSync("/tmp/vmfix/terse.json", JSON.stringify([...terse.values()], null, 1));
// sample fronts by length
const fronts = [...terse.values()].map(v=>v.front);
const short = fronts.filter(f=>f.split(" ").length<=3);
console.log("very short prompts (<=3 words):", short.length, short.slice(0,15));
