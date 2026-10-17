#!/usr/bin/env bash
# Write Chet's workout plan to the hub's Fitness tab (validmed.org/chet).
# Usage: set-workout-plan.sh plan.json
# plan.json shape:
#   {"date":"2026-10-17","name":"Upper B","items":[{"ex":"Pull-up","target":"3x6-10","note":"optional"},...]}
# Exercise names should match the hub chips (e.g. "Pull-up", "Seated cable row").
# Merges the plan into the existing chethub sync slot (GET -> set key -> POST),
# so shelf log, lift log and todos are preserved. No git push needed.
set -euo pipefail
SLOT='https://validmed.org/api/sync?name=chethub'
tmp=$(mktemp)
curl -sf "$SLOT" > "$tmp"
python3 - "$tmp" "$1" <<'PY'
import json,sys,urllib.request
cur=json.load(open(sys.argv[1]))
state=cur.get('state') or {}
plan=open(sys.argv[2]).read()
json.loads(plan)  # validate JSON before writing
state['chet_workout_plan']=plan
req=urllib.request.Request('https://validmed.org/api/sync?name=chethub',
    data=json.dumps({'state':state}).encode(),
    headers={'Content-Type':'application/json'}, method='POST')
print(urllib.request.urlopen(req).read().decode())
PY
rm -f "$tmp"
