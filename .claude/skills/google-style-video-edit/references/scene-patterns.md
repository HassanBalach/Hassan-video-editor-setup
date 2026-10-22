# Scene patterns

Every pattern below exists, working, in `examples/fsc-after-what-next/public/index.html` — the comment
headers (`<!-- ===== X. … ===== -->` in the HTML and `// ===== X. …` in the script) mark each one. Copy the
markup + timeline block, change the text and the times (edited-timeline seconds from `scripts/captions.py`).

Helpers available in the template script:

| helper | what it does |
| ------ | ------------ |
| `mode("full" \| "card" \| "pip", t, d)` | morphs `#video-wrap` (clip-path inset + y + scale) |
| `chrome("#card-shadow" \| "#pip-ring", t0, t1)` | fades the card shadow/ring or the spinning colour ring in and out |
| `layer(sel, t0, t1)` | shows a scene layer for a window |
| `popIn(sel, t)` | spring pop with y offset |
| `drawPath(sel, t, d)` | SVG stroke draw |
| `typeText(sel, text, t, cps)` | typewriter into an element |
| `blink(sel, t0, t1)` | caret blink with finite repeats |

| id | pattern | when to use | key pieces |
| -- | ------- | ----------- | ---------- |
| A | **Hook pill**: four dots bounce, pill stretches, title slides in; avatar cluster | first 2 s; who the video is for | `#hook-pill` width tween, `.hd` stagger, `.fr` avatars |
| B | **Search + suggestions** (video → card) | the audience's questions | `#search-bar`, `typeText`, `#sugg` dropdown, `.sg-hl` highlight sweep per question as it is spoken |
| C | **Confusion**: floating "?" badges, scribble draw, "No answers found" shake | relatable struggle | `.q` bob loops, `#scribble` drawPath, x-shake yoyo |
| D | **Circle-iris hero** that closes into a top pill | a big announcement ("One advice") | `clip-path: circle(0→1150px)` then `circle(0px at 540px 230px)` + pill pop |
| — | **Chips row** | a short list said quickly | `.chip` with colour dot, `popIn` per item |
| E | **Ripple hero** (video → pip circle, colour ring, 4 ripples, 3 stacked words, drawn underline) | the core mantra | `mode("pip")`, `.ripple` scale 1→2.3, `.ep-w` blur-in stagger, `#ep-line` |
| E2 | **Mountain climb**: ridge draws, dot climbs waypoints, flag pops | resilience / progress | precomputed waypoints (never measure DOM at tween time) |
| F | **Count-up bars** (video → card) | any percentage / number comparison | `scaleX` from 0 with `transform-origin:left`, counter object + `onUpdate` |
| G | **Colour-block wipe** | topic change; swap layout underneath while covered | 4 `.blk` columns `yPercent 100→0→-100`, `tl.set` the new mode at the midpoint |
| H | **AI chat**: language bubbles → dashed links → sparkle; equation card with gradient sweep; prompt types → typing dots → app tiles assemble → "Built" | tech / AI explanation | `.bubble`, `.lk` dash offset, `#eq-grad` background-position, `.tile` stagger |
| I | **YES**: question card, green circle scales in, check draws, seeded confetti | an answer / payoff | `#yes-c` scale, `#yes-ck` drawPath, PRNG `s = s*16807 % 2147483647` |
| J | **Flip comparison cards** | A vs B | `perspective` on the layer, `rotationY ±80→0`, dim the first when the second lands |
| K | **Skills hub**: centre node, 4 coloured satellites, lines draw from centre as each is said | a list of 3–5 qualities | `.skl` dash draw, `.sk` pop + bob |
| L | **Outro**: white circle iris, four dots, mantra, takeaway, CTA pill pulse | last 3 s | `#L` clip-path, `.od` stagger |
| — | **Captions** | always | built from `window.CAPS` at load; hidden during heroes via `hide.json` |

When inventing a new pattern, keep to the style guide: white rounded cards with soft shadow, brand colours,
Outfit, Material eases, entrances only (exits come from the next transition), and one SFX cue per event.
