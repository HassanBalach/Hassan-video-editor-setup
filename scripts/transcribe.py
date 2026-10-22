# Step 1: split the raw video into speech chunks at silences and transcribe each chunk.
# usage: python3 scripts/transcribe.py <raw.mp4> <work_dir> [lang=hi] [task=translate]
# writes: <work>/audio16.wav, <work>/chunks.json  [{i, start, end, text}]
import sys, os, json, wave, subprocess, re, numpy as np, sherpa_onnx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, work = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "hi"
task = sys.argv[4] if len(sys.argv) > 4 else "translate"   # translate -> English text (best for Urdu/Hindi speech)
os.makedirs(work, exist_ok=True)
wav = os.path.join(work, "audio16.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)

# silences (-35 dB, >= 0.4 s)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=n=-35dB:d=0.4", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
vals = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", log)]
sil = list(zip(vals[0::2], vals[1::2]))

w = wave.open(wav); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
dur = len(a) / sr
speech, t = [], 0.0
for s, e in sil:
    if s > t + 0.15: speech.append([t, s])
    t = e
if dur > t + 0.15: speech.append([t, dur])
# whisper handles <= 30 s windows; split longer chunks
chunks = []
for s, e in speech:
    while e - s > 28: chunks.append([s, s + 28]); s += 28
    chunks.append([s, e])

M = os.path.join(ROOT, "models/sherpa-onnx-whisper-medium/")
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M + "medium-encoder.int8.onnx", decoder=M + "medium-decoder.int8.onnx",
                                                 tokens=M + "medium-tokens.txt", language=lang, task=task, num_threads=os.cpu_count() or 4)
out = []
for i, (s, e) in enumerate(chunks):
    st = rec.create_stream(); st.accept_waveform(sr, a[int(s * sr):int(e * sr)]); rec.decode_stream(st)
    x = a[int(s * sr):int(e * sr)]
    db = round(float(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)), 1)
    out.append({"i": i, "start": round(s, 2), "end": round(e, 2), "db": db, "text": st.result.text.strip()})
    print(f"{i:3d} [{s:7.2f}-{e:7.2f}] {db:6.1f}dB  {out[-1]['text']}", flush=True)
json.dump(out, open(os.path.join(work, "chunks.json"), "w"), ensure_ascii=False, indent=1)
print("\nNext: review chunks.json, list chunk ids to DROP (silence, noise, false starts, repeats), then run cut.py")
