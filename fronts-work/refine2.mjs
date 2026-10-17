import fs from "fs";
const hand = JSON.parse(fs.readFileSync("/tmp/vmfix/hand.json","utf8"));

const TAILS = {
  "treatment":        t=>`What is the treatment for ${t}?`,
  "tx":               t=>`What is the treatment for ${t}?`,
  "management":       t=>`How is ${t} managed?`,
  "mechanism":        t=>`What is the mechanism of ${t}?`,
  "cause":            t=>`What is the cause of ${t}?`,
  "causes":           t=>`What are the causes of ${t}?`,
  "etiology":         t=>`What is the cause of ${t}?`,
  "diagnosis":        t=>`How is ${t} diagnosed?`,
  "workup":           t=>`How is ${t} worked up?`,
  "definition":       t=>`What is the definition of ${t}?`,
  "murmur":           t=>`What murmur is associated with ${t}?`,
  "presentation":     t=>`How does ${t} present?`,
  "findings":         t=>`What are the key findings in ${t}?`,
  "features":         t=>`What are the key features of ${t}?`,
  "labs":             t=>`What labs are seen in ${t}?`,
  "imaging":          t=>`What imaging is used for ${t}?`,
  "complications":    t=>`What are the complications of ${t}?`,
  "side effects":     t=>`What are the side effects of ${t}?`,
  "adverse effects":  t=>`What are the adverse effects of ${t}?`,
  "risk factors":     t=>`What are the risk factors for ${t}?`,
  "triad":            t=>`What is the classic triad of ${t}?`,
  "pathophysiology":  t=>`What is the pathophysiology of ${t}?`,
  "epidemiology":     t=>`What is the epidemiology of ${t}?`,
  "prognosis":        t=>`What is the prognosis of ${t}?`,
};
const tailKeys = Object.keys(TAILS).sort((a,b)=>b.length-a.length);

function lcTopic(topic) {
  // lowercase leading word unless acronym/proper (ALLCAPS, contains digit, or internal capital)
  const w = topic.split(/\s+/);
  if (!/^[A-Z0-9]{2,}$/.test(w[0]) && !/\d/.test(w[0]) && !/^[A-Z][a-z]*[A-Z]/.test(w[0])) {
    w[0] = w[0][0].toLowerCase()+w[0].slice(1);
  }
  return w.join(" ");
}

function tierB(f) {
  const base = f.replace(/\?+$/,"").trim();
  if (/\band\b\s*$/i.test(base) || /\band\b[^?]*\b(treatment|mechanism|cause|diagnosis|management|imaging|workup|presentation|findings|labs)\b/i.test(base)) return null;
  if (/\b(vignette|figure|source|repeat|continued)\b/i.test(base)) return null;
  let m = base.match(/^(.+?):\s*([A-Za-z ]+)$/);
  if (m) {
    const tail = m[2].trim().toLowerCase();
    if (TAILS[tail]) return TAILS[tail](lcTopic(m[1].trim()));
    return null;
  }
  for (const tk of tailKeys) {
    if (base.toLowerCase().endsWith(" "+tk)) {
      const topic = base.slice(0, base.length-tk.length).trim();
      if (topic.length < 3) return null;
      if (!/\s/.test(topic) && !/[A-Z]/.test(topic.slice(1))) return null;
      return TAILS[tk](lcTopic(topic));
    }
  }
  return null;
}

const bOut = [], rest = [];
for (const t of hand) {
  const conv = tierB(t.front);
  if (conv) bOut.push({...t, converted: conv}); else rest.push(t);
}
console.log("tier-B converted:", bOut.length, "| remaining hand:", rest.length);
fs.writeFileSync("/tmp/vmfix/tierB.json", JSON.stringify(bOut, null, 1));
fs.writeFileSync("/tmp/vmfix/hand2.json", JSON.stringify(rest, null, 1));
for (let i=0;i<bOut.length;i+=Math.ceil(bOut.length/15)) console.log("  "+bOut[i].front+"  ==>  "+bOut[i].converted);
const per = {}; for (const t of rest) for (const it of t.items) per[it.bank]=(per[it.bank]||0)+1;
console.log("remaining instances per bank:", per);
