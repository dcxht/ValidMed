import fs from "fs";
const terse = JSON.parse(fs.readFileSync("/tmp/vmfix/terse.json","utf8"));
const n = parseInt(process.argv[2], 10);
const size = parseInt(process.argv[3]||"75", 10);
const batch = terse.slice(n, n+size);
batch.forEach((t,i)=>{
  const a = t.items[0].a.replace(/\s+/g," ").slice(0, 350);
  console.log(`#${n+i} [${t.items[0].bank} ${t.items.length>1?"x"+t.items.length:"1"}] ${t.front}`);
  console.log(`   A: ${a}`);
});
console.log(`-- batch ${n}..${n+batch.length-1} of ${terse.length}`);
