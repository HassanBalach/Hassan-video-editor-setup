# Step 3: turn hand-written captions (per transcript chunk) into timed caption groups on the EDITED timeline.
# usage: python3 scripts/captions.py <work_dir> <project_dir>
# reads:  <work>/chunks.json, <work>/segments.json, <project>/captions.json  {"<chunk id>": "text with [keywords]"}
#         optional <project>/hide.json  [[t0, t1], ...]  edited-timeline windows with no captions (full-screen hero cards)
# writes: <project>/public/captions.js  (window.CAPS = [[t0, t1, [[word, colourIdx|-1], ...]], ...])
import sys, os, json

work, proj = sys.argv[1], sys.argv[2]
segs = json.load(open(os.path.join(work, "segments.json")))
CH = {c["i"]: c for c in json.load(open(os.path.join(work, "chunks.json")))}
CAPTIONS = {int(k): v for k, v in json.load(open(os.path.join(proj, "captions.json"))).items()}
hp = os.path.join(proj, "hide.json")
HIDE = json.load(open(hp)) if os.path.exists(hp) else []

cum, acc = [], 0.0
for s, e in segs: cum.append(acc); acc += e - s
def m(t):  # source seconds -> edited seconds
    for k, (s, e) in enumerate(segs):
        if t < s: return cum[k]
        if t <= e: return cum[k] + t - s
    return acc

caps, ci = [], 0
for i, txt in sorted(CAPTIONS.items()):
    words = [[w.replace("[", "").replace("]", ""), "[" in w or "]" in w] for w in txt.split()]
    groups, cur = [], []
    for w in words:  # <= 3 words / ~17 chars per caption
        if cur and (len(cur) >= 3 or sum(len(x[0]) + 1 for x in cur) + len(w[0]) > 17): groups.append(cur); cur = []
        cur.append(w)
    if cur: groups.append(cur)
    s, e = CH[i]["start"], CH[i]["end"]
    tot = sum(sum(len(x[0]) + 2 for x in g) for g in groups); a = 0
    for g in groups:
        L = sum(len(x[0]) + 2 for x in g)
        t0, t1 = m(s + (e - s) * a / tot), m(s + (e - s) * (a + L) / tot); a += L
        out = []
        for w, hl in g:
            out.append([w, ci % 4 if hl else -1]); ci += hl
        caps.append([round(t0, 3), round(t1, 3), out])
caps.sort(key=lambda c: c[0])
for k in range(len(caps) - 1):
    if caps[k + 1][0] - caps[k][1] < 0.4: caps[k][1] = caps[k + 1][0]
caps = [c for c in caps if not any(a <= c[0] < b for a, b in HIDE)]
for c in caps:
    for a, b in HIDE:
        if c[0] < a < c[1]: c[1] = a
os.makedirs(os.path.join(proj, "public"), exist_ok=True)
open(os.path.join(proj, "public/captions.js"), "w").write("window.CAPS = " + json.dumps(caps, ensure_ascii=False) + ";\n")

# chunk start/end on the edited timeline: use these numbers when timing animations in index.html
print(f"{len(caps)} caption groups, edited length {acc:.2f}s\n\nchunk  start   end   text")
for i, c in CH.items():
    print(f"{i:4d} {m(c['start']):7.2f} {m(c['end']):7.2f}  {c['text'][:70]}")
