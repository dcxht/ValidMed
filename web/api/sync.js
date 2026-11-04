// Server-side memory for personal copies (/c, /jai, ...), keyed by link name.
// No accounts, no login: the link IS the slot. Free Upstash Redis via Vercel
// Marketplace injects KV_REST_API_URL / KV_REST_API_TOKEN when connected.
const URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const NAME_RE = /^[a-z]{1,20}$/;
const MAX_BYTES = 900000;

// chethub shelf-log merge: one atomic EVAL (no read/write race). Rules per day,
// per field: incoming wins; null is a persistent clear-tombstone (old-client
// omission can never resurrect it); omitted fields keep cloud values; cloud-only
// days kept. A malformed incoming day never replaces a healthy cloud day; a
// malformed incoming log or an EVAL failure aborts with NO write (return 0 ->
// 502) - fail CLOSED, never an unmerged overwrite. A chethub POST that omits
// chet_shelf_log carries the cloud's forward instead of wiping it. The client
// retains its data locally, flags it unsynced, and retries. There is no
// plain-SET path for this slot's shelf log. Other slots keep legacy SET.
const MERGE_LUA = "local cur=redis.call('GET',KEYS[1]) local st=cjson.decode(ARGV[1]) local inc=st['chet_shelf_log'] if cur then local ok,cs=pcall(cjson.decode,cur) if ok and type(cs)=='table' and type(cs['chet_shelf_log'])=='string' then if type(inc)=='string' then local okc,cl=pcall(cjson.decode,cs['chet_shelf_log']) local oki,il=pcall(cjson.decode,inc) if okc and oki and type(cl)=='table' and type(il)=='table' then for day,rec in pairs(il) do local prev=cl[day] if type(rec)=='table' then if type(prev)=='table' then for k,v in pairs(rec) do prev[k]=v end cl[day]=prev else cl[day]=rec end end end st['chet_shelf_log']=cjson.encode(cl) else return 0 end else st['chet_shelf_log']=cs['chet_shelf_log'] end end end redis.call('SET',KEYS[1],cjson.encode(st)) return 1";

async function redis(cmd) {
  const r = await fetch(`${URL}/${cmd.map(encodeURIComponent).join("/")}`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  if (!r.ok) throw new Error(`redis ${r.status}`);
  const j = await r.json();
  if (j && j.error) throw new Error(`redis: ${j.error}`);
  return j;
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (!URL || !TOKEN) {
    res.status(503).json({ error: "storage not connected" });
    return;
  }
  const name = (req.query.name || "").toLowerCase();
  if (!NAME_RE.test(name)) {
    res.status(400).json({ error: "bad name" });
    return;
  }
  const k = `vm:${name}`;
  try {
    if (req.method === "GET") {
      const { result } = await redis(["get", k]);
      res.status(200).json({ state: result ? JSON.parse(result) : null });
      return;
    }
    if (req.method === "POST") {
      let body = "";
      for await (const chunk of req) body += chunk;
      if (body.length > MAX_BYTES) {
        res.status(413).json({ error: "too big" });
        return;
      }
      const { state } = JSON.parse(body);
      // Every chethub POST goes through the atomic merge (an omitted shelf log
      // carries the cloud copy forward, never wipes it). Other slots: plain SET.
      if (name === "chethub" && state && typeof state === "object") {
        // one retry for transient REST hiccups, then fail closed: no write, no
        // non-atomic fallback. The client keeps its local copy and retries.
        for (let attempt = 0; attempt < 2; attempt++) {
          try {
            const r = await redis(["eval", MERGE_LUA, "1", k, JSON.stringify(state)]);
            if (r && r.result === 1) {
              res.status(200).json({ ok: true });
              return;
            }
            // script refused (e.g. malformed incoming log): nothing was written
            break;
          } catch (e) {
            // transient failure: loop retries once
          }
        }
        res.status(502).json({ error: "merge unavailable" });
        return;
      }
      await redis(["set", k, JSON.stringify(state)]);
      res.status(200).json({ ok: true });
      return;
    }
    res.status(405).json({ error: "method" });
  } catch (e) {
    res.status(502).json({ error: "storage error" });
  }
}
