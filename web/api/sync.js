// Server-side memory for personal copies (/c, /jai, ...), keyed by link name.
// No accounts, no login: the link IS the slot. Free Upstash Redis via Vercel
// Marketplace injects KV_REST_API_URL / KV_REST_API_TOKEN when connected.
const URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const NAME_RE = /^[a-z]{1,20}$/;
const MAX_BYTES = 900000;

async function redis(cmd) {
  const r = await fetch(`${URL}/${cmd.map(encodeURIComponent).join("/")}`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  if (!r.ok) throw new Error(`redis ${r.status}`);
  return r.json();
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
      await redis(["set", k, JSON.stringify(state)]);
      res.status(200).json({ ok: true });
      return;
    }
    res.status(405).json({ error: "method" });
  } catch (e) {
    res.status(502).json({ error: "storage error" });
  }
}
