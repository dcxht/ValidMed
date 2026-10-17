import fs from "fs";
const banks = JSON.parse(fs.readFileSync("/tmp/vmfix/banks.json","utf8"));
const PG = String.raw`pp?\.?\s*\d{1,3}(?:\s*[-–]\s*\d{1,3})?`;

export function stripPageRefs(q) {
  let s = q;
  s = s.replace(new RegExp(String.raw`\s*\((?:continues?|continued)\s+(?:from\s+|on\s+)?${PG}\)`,"gi"), "");
  s = s.replace(new RegExp(String.raw`\s+per\s+${PG}(\s*[:?,.])?\s*$`,"i"), (m,p1)=>p1||"");
  s = s.replace(new RegExp(String.raw`\s+per\s+${PG}\s*:\s*`,"gi"), ": ");
  s = s.replace(new RegExp(String.raw`\s+per\s+${PG}\s*,\s*`,"gi"), ", ");
  s = s.replace(new RegExp(String.raw`\s+per\s+${PG}\s+`,"gi"), " ");
  s = s.replace(new RegExp(String.raw`\bon\s+${PG}\b`,"gi"), "in the source");
  s = s.replace(new RegExp(String.raw`\bthe\s+${PG}\b`,"gi"), "the source");
  s = s.replace(new RegExp(String.raw`\bsource\s+${PG}\b`,"gi"), "source");
  s = s.replace(new RegExp(String.raw`\b${PG}\b`,"g"), "the source");
  s = s.replace(/\bthe\s+the\s+source\b/gi, "the source");
  s = s.replace(/\b(a|an)\s+the\s+source\b/gi, "the source");
  s = s.replace(/\bsource\s+the\s+source\b/gi, "source");
  s = s.replace(/\b(Which|What|How|Whose)\s+the\s+source\s+(?!(?:give|gives|say|says|list|lists|describe|describes|mean|means|call|calls|make|makes|is|are|was|were|does|do|did|claim|claims|state|states|teach|teaches|show|shows|name|names|associate|associates|choose|chooses|warn|warns|define|defines|emphasize|emphasizes|select|selects|infer|infers|equate|equates|contrast|contrasts|repeat|repeats|advise|advises|print|prints|present|presents|consider|considers|add|adds|link|links|use|uses)\b)/gi, "$1 source ");
  s = s.replace(/\s{2,}/g, " ").replace(/\s+([?:,;.])/g, "$1").trim();
  if (s.length) s = s[0].toUpperCase()+s.slice(1);
  return s;
}

const changed = [], leftover = [];
for (const [bank, cards] of Object.entries(banks)) {
  for (const c of cards) {
    const nq = stripPageRefs(c.q);
    if (nq !== c.q) changed.push({bank, id:c.id, old:c.q, now:nq});
    if (new RegExp(String.raw`\b${PG}\b`).test(nq)) leftover.push({bank, id:c.id, q:nq});
    const na = stripPageRefs(c.a);
    if (new RegExp(String.raw`\b${PG}\b`).test(na)) leftover.push({bank, id:c.id, a:na});
  }
}
console.log("fronts changed:", changed.length, "| leftover p-refs:", leftover.length);
leftover.slice(0,10).forEach(l=>console.log(" LEFT:", l.bank, l.id, l.q||l.a));
fs.writeFileSync("/tmp/vmfix/changed.json", JSON.stringify(changed, null, 1));
// re-show prior problem cards
for (const id of ["s2peds-0700","s2peds-1567","s2med-1879","s2med-3358","s2med-3697","s2med-3974","s2peds-2620","s2obgyn-0423","s2peds-1658"]) {
  const c = changed.find(x=>x.id===id); if (c) console.log("CHK", id, "=>", c.now);
}
