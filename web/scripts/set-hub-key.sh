#!/usr/bin/env bash
# Write an arbitrary JSON key into the hub's chethub sync slot (validmed.org/chet).
# Usage: set-hub-key.sh <key> <json-file>
# Example: set-hub-key.sh chet_week_plan week-plan.json
#   week-plan.json: {"groups":{"Back":12,"Chest":6,"Shoulders":9,"Arms":12,"Legs":10,"Core":4}}
# Merges into the slot (GET -> set key -> POST); all other keys preserved. No git push.
set -euo pipefail
KEY="$1"; FILE="$2"
SLOT='https://validmed.org/api/sync?name=chethub'
tmp=$(mktemp)
curl -sf "$SLOT" > "$tmp"
python3 - "$tmp" "$KEY" "$FILE" <<'PY'
import json,sys,urllib.request
cur=json.load(open(sys.argv[1]))
state=cur.get('state') or {}
val=open(sys.argv[3]).read()
json.loads(val)  # validate JSON before writing
state[sys.argv[2]]=val
req=urllib.request.Request('https://validmed.org/api/sync?name=chethub',
    data=json.dumps({'state':state}).encode(),
    headers={'Content-Type':'application/json'}, method='POST')
print(urllib.request.urlopen(req).read().decode())
PY
rm -f "$tmp"
