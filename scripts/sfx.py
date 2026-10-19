# Synthesized sound effects (original, no licence needed) placed at the render's event times.
import sys, json, wave, numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
ev = json.load(open(sys.argv[1])); DUR = float(sys.argv[3])
rng = np.random.default_rng(3)
def T(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x)

def whoosh(d=0.45):
    t = T(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t)
    # sweep a band-pass upwards by processing short blocks
    blk = 1024
    for i in range(0, len(t), blk):
        f = 300 + 3500 * (i / len(t)) ** 1.5
        out[i:i + blk] = bp(n[i:i + blk + 0], f * 0.6, min(f * 1.6, 20000))[:len(out[i:i + blk])]
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * env * 1.6
def swoosh_soft(): return whoosh(0.3) * 0.6
def pop():
    t = T(0.12); f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35) * 0.8
def tick():
    t = T(0.05); return hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 120) * 0.5
def ding():
    t = T(1.4); f = 1318.5
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.5 + 2 * k)) for k, a in [(1, 1), (2.01, .4), (3.0, .2), (4.2, .1)])
    return s * np.minimum(1, t / 0.003) * 0.45
def hit():
    t = T(0.6); f = 45 + 90 * np.exp(-t * 18)
    b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    n = bp(rng.standard_normal(len(t)), 200, 3000) * np.exp(-t * 20) * 0.4
    return (b + n) * 0.8
def flash():
    t = T(0.25); return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 18) * 0.35
def rise():
    t = T(0.8); f = 300 + 900 * (t / 0.8) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / 0.8) * np.exp(-np.maximum(0, t - 0.7) * 40) * 0.25

GEN = dict(whoosh=whoosh, swoosh_soft=swoosh_soft, pop=pop, tick=tick, ding=ding, hit=hit, flash=flash, rise=rise)
out = np.zeros(int(DUR * SR) + SR)
for t, k, g in ev:
    s = GEN[k]() * g; i = int(t * SR)
    if 0 <= i < len(out): out[i:i + len(s)] += s[:len(out) - i]
out = out[:int(DUR * SR)]
out = out / max(1e-9, np.abs(out).max()) * 0.7
w = wave.open(sys.argv[2], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close(); print("sfx events", len(ev))
