#!/usr/bin/env bash
# Rate a workout session 1-10 (shows in the hub's This week / Past weeks).
# Usage: rate-session.sh <date YYYY-MM-DD> <rating 1-10>
# Example: rate-session.sh 2026-10-17 8
# Merges the rating into chet_session_ratings in the chethub slot. No git push.
set -euo pipefail
DATE="$1"; RATING="$2"
SLOT='https://validmed.org/api/sync?name=chethub'
tmp=$(mktemp)
curl -sf "$SLOT" > "$tmp"
python3 - "$tmp" "$DATE" "$RATING" <<'PY'
import json,sys,urllib.request
cur=json.load(open(sys.argv[1]))
state=cur.get('state') or {}
try:
    ratings=json.loads(state.get('chet_session_ratings') or '{}')
except Exception:
    ratings={}
r=float(sys.argv[3])
if not (1<=r<=10): raise SystemExit('rating must be 1-10')
ratings[sys.argv[2]]=int(r) if r==int(r) else r
state['chet_session_ratings']=json.dumps(ratings)
req=urllib.request.Request('https://validmed.org/api/sync?name=chethub',
    data=json.dumps({'state':state}).encode(),
    headers={'Content-Type':'application/json'}, method='POST')
print(urllib.request.urlopen(req).read().decode())
PY
rm -f "$tmp"
