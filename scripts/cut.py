# Step 2: denoise the voice, drop unwanted chunks, cut every silence, upscale to 1080x1920 HD.
# usage: python3 scripts/cut.py <raw.mp4> <work_dir> --drop 0,1,2,15
# writes: <work>/clean.wav, <work>/segments.json (kept source intervals), <work>/edited_HD.mp4
import sys, os, json, re, subprocess, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("work")
ap.add_argument("--drop", default="", help="comma-separated chunk ids to remove")
ap.add_argument("--pad-in", type=float, default=0.12); ap.add_argument("--pad-out", type=float, default=0.15)
ap.add_argument("--keep-pause", type=float, default=0.12, help="seconds of pause kept on each side of a cut")
args = ap.parse_args()
W = args.work
drop = {int(x) for x in args.drop.split(",") if x.strip()}
chunks = json.load(open(os.path.join(W, "chunks.json")))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.src],
                           capture_output=True, text=True).stdout)

# 1) clean voice: rumble/hiss filters, RNNoise, FFT denoise, gentle compression, -14 LUFS
clean = os.path.join(W, "clean.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.src, "-vn", "-af",
                f"highpass=f=80,lowpass=f=12000,arnndn=m={ROOT}/models/rnnoise.rnnn:mix=0.9,afftdn=nr=10:nf=-40,"
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=9",
                "-ar", "48000", "-ac", "1", clean], check=True)

# 2) kept intervals from chunks
segs = []
for c in chunks:
    if c["i"] in drop: continue
    s, e = max(0, c["start"] - args.pad_in), min(dur, c["end"] + args.pad_out)
    if segs and s <= segs[-1][1] + 0.05: segs[-1][1] = e
    else: segs.append([s, e])

# 3) tighten pauses inside kept speech (detected on the denoised track)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", clean, "-af", "silencedetect=n=-38dB:d=0.4", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
vals = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", log)]
for a, b in zip(vals[0::2], vals[1::2]):
    a += args.keep_pause; b -= args.keep_pause
    if b - a < 0.15: continue
    new = []
    for s, e in segs:
        if b <= s or a >= e: new.append([s, e]); continue
        if a > s + 0.2: new.append([s, a])
        if b < e - 0.2: new.append([b, e])
    segs = new
json.dump(segs, open(os.path.join(W, "segments.json"), "w"))

# 4) one ffmpeg pass: trim+concat, 15 ms fades on every cut, lanczos upscale + light sharpen
parts, cat = [], ""
for i, (s, e) in enumerate(segs):
    d = e - s
    parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}];")
    parts.append(f"[1:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.02:.3f}:d=0.02[a{i}];")
    cat += f"[v{i}][a{i}]"
fc = "".join(parts) + cat + (f"concat=n={len(segs)}:v=1:a=1[vc][ac];[vc]fps=30,scale=1080:1920:flags=lanczos,"
                             "unsharp=5:5:0.6:5:5:0.0,eq=contrast=1.04:saturation=1.06,format=yuv420p[vout]")
open(os.path.join(W, "cut_filter.txt"), "w").write(fc)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.src, "-i", clean, "-filter_complex_script", os.path.join(W, "cut_filter.txt"),
                "-map", "[vout]", "-map", "[ac]", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", os.path.join(W, "edited_HD.mp4")], check=True)
print(f"{len(segs)} segments, {sum(e - s for s, e in segs):.1f}s kept of {dur:.1f}s -> {W}/edited_HD.mp4")
