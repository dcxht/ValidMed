import fs from "fs";
const banks = { s2fm:"familyMedicine", s2psy:"psychiatry", s2neuro:"neurology", s2peds:"pediatrics", s2med:"medicine", s2surg:"surgery", s2obgyn:"obgyn" };
const out = {};
for (const [bank, f] of Object.entries(banks)) {
  const mod = await import(`file:///tmp/validmed/web/src/data/step2/${f}.js`);
  out[bank] = mod.default;
}
fs.writeFileSync("/tmp/vmfix/banks.json", JSON.stringify(out, null, 1));
let n=0; for (const b of Object.values(out)) n+=b.length;
console.log("parsed", n, "cards");
