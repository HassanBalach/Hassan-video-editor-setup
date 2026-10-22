#!/usr/bin/env bash
# Start a new video project: copies the raw video in, transcribes it, prints the next steps.
# usage: scripts/new.sh <raw.mp4> <name>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$1"; NAME="$2"
W="$ROOT/work/$NAME"; P="$ROOT/projects/$NAME"
mkdir -p "$W" "$P"
cp --update=none "$SRC" "$W/raw.mp4"
python3 "$ROOT/scripts/transcribe.py" "$W/raw.mp4" "$W"
cat <<EOF

Project "$NAME" started.
  work files : $W   (raw.mp4, chunks.json)
  project    : $P   (captions.json, sfx_events.json, public/index.html go here)

Next:
  1. pick chunk ids to drop from $W/chunks.json
  2. python3 scripts/cut.py $W/raw.mp4 $W --drop <ids>
  3. scripts/stage.sh $W $P
  4. write $P/captions.json (+ hide.json), then python3 scripts/captions.py $W $P
  5. build scenes in $P/public/index.html, cues in $P/sfx_events.json
  6. scripts/render.sh $W $P
EOF
