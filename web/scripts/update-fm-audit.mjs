import fs from 'node:fs';
const root=new URL('../',import.meta.url);
const src=fs.readFileSync(new URL('src/data/step2/familyMedicine.js',root),'utf8');
const cs=JSON.parse(src.split('export default ')[1].replace(/;\s*$/,''));
const byId=new Map(cs.map(x=>[x.id,x]));
const active=cs.filter(x=>!x.duplicateOf);
for(const q of cs.filter(x=>x.duplicateOf))if(!byId.has(q.duplicateOf)||byId.get(q.duplicateOf).duplicateOf)throw Error(`Invalid canonical target ${q.id}`);
const mapURL=new URL('content-audit/family-medicine-duplicate-map.json',root);
const map=JSON.parse(fs.readFileSync(mapURL,'utf8'));
map.duplicates=cs.filter(x=>x.duplicateOf).map(x=>({retired:x.id,active:x.duplicateOf,retiredPage:x.source.page,activePage:byId.get(x.duplicateOf).source.page}));
fs.writeFileSync(mapURL,JSON.stringify(map,null,2)+'\n');
const rows=['# FM source-page mapping','','All source locations after semantic consolidation. This is a locator index, not proof that every fact was independently verified. Source pp4-317 read three times; p184 repeats dementia/Parkinson/RLS from earlier pages and no count-padding card was added.','','| PDF page | Active card IDs | Figure cards | Linked verification notes |','|---|---|---|---|'];
for(let p=4;p<=317;p++){const qs=active.filter(x=>(x.sourcePages||[x.source.page]).includes(p));rows.push(`| ${p} | ${qs.map(x=>x.id).join(', ')||'Repetition: pp146-148 plus NPH continuation'} | ${qs.filter(x=>x.img).length} | ${qs.filter(x=>x.guideline).length} |`)}
fs.writeFileSync(new URL('content-audit/family-medicine-page-map.md',root),rows.join('\n')+'\n');
console.log(JSON.stringify({historical:cs.length,active:active.length,retired:cs.length-active.length,figures:active.filter(x=>x.img).length,notes:active.filter(x=>x.guideline).length}));
