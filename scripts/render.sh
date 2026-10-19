#!/usr/bin/env bash
# Step 5: render the HyperFrames composition, then mix voice + ducked music + SFX and mux.
# usage: scripts/render.sh <work_dir> <project_dir>
#   needs <project>/public/index.html (+ input-video.mp4 staged by stage.sh) and <project>/sfx_events.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
W="$(cd "$1" && pwd)"; P="$(cd "$2" && pwd)"
HF="npx --prefix $ROOT hyperframes"

$HF lint "$P/public"
$HF render "$P/public" -o "$P/render_hf.mp4" --fps 30 --quality looks

D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/render_hf.mp4")
python3 -I "$ROOT/scripts/music.py" "$W/music.wav" "$D"
python3 -I "$ROOT/scripts/sfx.py" "$P/sfx_events.json" "$W/sfx.wav" "$D"

# music -17 dB under the voice and side-chain ducked whenever the voice is present
ffmpeg -v error -y -i "$W/edited_HD.mp4" -i "$W/music.wav" -i "$W/sfx.wav" -filter_complex \
  "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur=$D,asplit=2[v][sc];\
[1:a]volume=-17dB,apad=whole_dur=$D,atrim=0:$D[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[mud];\
[2:a]volume=-9dB,pan=stereo|c0=c0|c1=c0,apad=whole_dur=$D[fx];\
[v][mud][fx]amix=inputs=3:normalize=0:duration=first,atrim=0:$D,alimiter=limit=0.89,loudnorm=I=-14:TP=-1.5:LRA=11[out]" \
  -map "[out]" -ar 48000 "$W/mix.wav"
ffmpeg -v error -y -i "$W/edited_HD.mp4" -i "$W/sfx.wav" -filter_complex \
  "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur=$D[v];[1:a]volume=-9dB,pan=stereo|c0=c0|c1=c0,apad=whole_dur=$D[fx];\
[v][fx]amix=inputs=2:normalize=0:duration=first,atrim=0:$D,alimiter=limit=0.89,loudnorm=I=-14:TP=-1.5:LRA=11[out]" \
  -map "[out]" -ar 48000 "$W/mix_nomusic.wav"

ffmpeg -v error -y -i "$P/render_hf.mp4" -i "$W/mix.wav" -map 0:v -map 1:a -c:v libx264 -preset medium -crf 20 \
  -maxrate 14M -bufsize 28M -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$P/final_with_music.mp4"
ffmpeg -v error -y -i "$P/final_with_music.mp4" -i "$W/mix_nomusic.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -shortest -movflags +faststart "$P/final_no_music.mp4"
ls -la "$P"/final_*.mp4
