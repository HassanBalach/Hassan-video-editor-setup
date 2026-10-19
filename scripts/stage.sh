#!/usr/bin/env bash
# Step 4: create a project folder for a new video from the template and stage the edited footage.
# usage: scripts/stage.sh <work_dir> <project_dir>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
W="$1"; P="$2"
mkdir -p "$P/public"
cp -rn "$ROOT/template/public/." "$P/public/"
# dense keyframes so the renderer can seek every frame
ffmpeg -v error -y -i "$W/edited_HD.mp4" -c:v libx264 -preset fast -crf 18 -g 30 -keyint_min 30 \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k "$P/public/input-video.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/public/input-video.mp4")
sed -i "s/data-duration=\"DURATION\"/data-duration=\"$(printf %.2f "$D")\"/g" "$P/public/index.html"
[ -f "$P/captions.json" ] || echo '{}' > "$P/captions.json"
[ -f "$P/sfx_events.json" ] || echo '[]' > "$P/sfx_events.json"
echo "staged -> $P/public  (now write captions.json, index.html scenes, sfx_events.json)"
