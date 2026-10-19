# Original, calm-uplifting lo-fi bed (C - G - Am - F), synthesized from scratch -> no copyright / no credit needed.
import sys, numpy as np, wave
SR = 48000
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 160.0
BPM = 88
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
# chords as midi notes (C major: I - V - vi - IV)
PROG = [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69], [41, 53, 57, 60, 65]]
ROOT = [36, 43, 45, 41]

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i]
    buf[i:i + len(sig)] += gain * sig

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)

def pad(notes, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for m in notes[1:]:
        f = hz(m)
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            s += np.sin(2 * np.pi * ff * t + ph) + 0.35 * np.sin(4 * np.pi * ff * t + ph) + 0.15 * np.sin(6 * np.pi * ff * t + ph)
    att, rel = 0.6, 0.8
    env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0, 1)
    return lowpass(s * env, 1400) / 12

def keys(m, dur=1.2):
    t = np.arange(int(dur * SR)) / SR
    f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.2 + 1.8 * k)) for k, a in [(1, 1), (2, .45), (3, .2), (4, .1)])
    s *= np.minimum(1, t / 0.004)
    return s

def bass(m, dur):
    t = np.arange(int(dur * SR)) / SR
    f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 1.6) * np.minimum(1, t / 0.01)

def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)

def hat():
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 6000)
    return n * np.exp(-t * 70)

def snap():
    t = np.arange(int(0.18 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = lowpass(n - lowpass(n, 1200), 5000)
    return n * np.exp(-t * 28) + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)

bars = int(np.ceil(DUR / BAR))
K, H, SN = kick(), hat(), snap()
arp_pat = [0, 2, 3, 4, 3, 2, 4, 3]  # indexes into chord tones (raised an octave)
for b in range(bars):
    t0 = b * BAR
    ch = PROG[b % 4]
    p = pad(ch, BAR + 0.8)
    add(L, t0, p, 1.0); add(R, t0, p, 1.0)
    full = 2 <= b < bars - 2
    if b >= 1:
        for k in range(8):
            if not full and k % 2: continue
            m = ch[arp_pat[k]] + 12
            s = keys(m)
            g = 0.16 if k % 2 == 0 else 0.11
            pan = 0.35 + 0.3 * (k % 2)
            add(L, t0 + k * BEAT / 2 + rng.uniform(0, 0.012), s, g * (1 - pan) * 2)
            add(R, t0 + k * BEAT / 2 + rng.uniform(0, 0.012), s, g * pan * 2)
    if full:
        for k in (0, 2.5):
            bs = bass(ROOT[b % 4], BEAT * 1.5)
            add(L, t0 + k * BEAT, bs, 0.28); add(R, t0 + k * BEAT, bs, 0.28)
        for k in (0, 2.5):
            add(L, t0 + k * BEAT, K, 0.30); add(R, t0 + k * BEAT, K, 0.30)
        for k in (1, 3):
            add(L, t0 + k * BEAT, SN, 0.10); add(R, t0 + k * BEAT, SN, 0.12)
        for k in range(8):
            g = 0.05 if k % 2 else 0.025
            sw = 0.03 if k % 2 else 0  # lazy swing
            add(L, t0 + k * BEAT / 2 + sw, H, g * 0.8); add(R, t0 + k * BEAT / 2 + sw, H, g * 1.2)

# simple reverb: decaying noise impulse response
ir_t = np.arange(int(1.8 * SR)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
ir = lowpass(ir, 4500); ir /= np.sqrt((ir ** 2).sum())
def conv(x):
    n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
L = L + 0.35 * conv(L); R = R + 0.35 * conv(R)

# lo-fi warmth + gentle fades
L, R = lowpass(L, 9000), lowpass(R, 9000)
t = np.arange(N) / SR
fade = np.minimum(1, t / 2.0) * np.minimum(1, (DUR - t) / 3.0).clip(0, 1)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
st = (np.stack([L, R], 1) / peak * 0.8 * 32767).astype(np.int16)
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print("music", DUR, "s")
