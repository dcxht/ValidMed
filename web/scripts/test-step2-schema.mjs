import fs from 'node:fs';
import assert from 'node:assert/strict';
const ids=new Set();
for(const file of fs.readdirSync(new URL('../src/data/step2/',import.meta.url)).filter(x=>x.endsWith('.js'))){
 const text=fs.readFileSync(new URL('../src/data/step2/'+file,import.meta.url),'utf8');
 const cards=JSON.parse(text.split('export default ')[1].replace(/;\s*$/,''));
 for(const q of cards){
  assert(!ids.has(q.id),`Duplicate ${q.id}`);ids.add(q.id);
  assert(q.q&&q.a&&q.category,`Missing content ${q.id}`);
  assert(!q.image,`Use img field: ${q.id}`);
  assert(q.source?.page&&q.source.url.endsWith('#page='+q.source.page),`Bad page ${q.id}`);
  const source=q.source.url.split('#')[0];assert(fs.existsSync(new URL('../public'+source,import.meta.url)),`Missing PDF ${q.id}`);
  if(q.img)assert(fs.existsSync(new URL('../public'+q.img,import.meta.url)),`Missing figure ${q.id}`);
  if(q.guideline)assert(q.guideline.text&&q.guideline.url.startsWith('https://'),`Bad note ${q.id}`);
 }
 console.log(file,cards.length,'records verified');
}
