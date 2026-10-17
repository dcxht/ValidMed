import fs from "fs";
const hand = JSON.parse(fs.readFileSync("/tmp/vmfix/hand2.json","utf8"));
const n = parseInt(process.argv[2], 10);
const size = parseInt(process.argv[3]||"100", 10);
hand.slice(n, n+size).forEach((t,i)=>{
  const a = t.items[0].a.replace(/\s+/g," ").slice(0, 300);
  console.log(`#${n+i} ${t.front}`);
  console.log(`   A: ${a}`);
});
console.log(`-- batch ${n}..${Math.min(n+size,hand.length)-1} of ${hand.length}`);
