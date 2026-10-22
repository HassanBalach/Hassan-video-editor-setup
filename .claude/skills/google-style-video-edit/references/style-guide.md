# Style guide

## Canvas and safe zones (1080×1920)

| zone | y range | used for |
| ---- | ------- | -------- |
| top bar | 150–290 | topic pills ("After FSC, what next?", "The only advice") |
| face (full mode) | ~300–1000 | keep clear; small accents only at the sides (x < 230 or x > 850) |
| content band | 980–1520 | cards, panels, chips, search bar, charts |
| captions | 1580–1710 | the caption pill, always |
| platform UI | > 1750 | nothing important (Shorts/Reels buttons and title cover it) |

In `card` mode the video occupies y 80–930, in `pip` mode a circle centred at (540, 340), radius ~180.

## Colour

```
--blue #4285f4   --red #ea4335   --yellow #fbbc05 (text: #e3a600)   --green #34a853
--ink #1f1f1f    --ink2 #5f6368  --paper #f8fafd  cards #ffffff
```

- Keywords in captions cycle blue → red → yellow → green.
- Each section leans on one accent (hero "One advice" = blue, "YES" = green, warnings = yellow).
- Behind the cropped video: paper background + four blurred colour blobs (blur 90px, 0.42 opacity) drifting slowly, plus a faint dot grid.

## Type

- **Outfit** (variable, 100–900) for everything; Noto Nastaliq Urdu for Urdu/Balochi script — put the script in its
  own `<span class="urdu" dir="rtl">` so Latin text stays in Outfit.
- Captions 62px weight 800 on a white pill (radius 34, soft shadow), ≤ 3 words / ~17 characters per caption.
- Heroes 140–170px weight 800, letter-spacing -3px; kickers 44px weight 600, uppercase, 6px tracking.
- Card titles 54–64px weight 800; body 36–48px weight 500–700.

## Motion (Material feel)

| use | ease | duration |
| --- | ---- | -------- |
| entrances, reveals | `expo.out` | 0.5–0.8 s |
| layout morphs (video mode changes) | `power3.inOut` | 0.9–1.0 s |
| pops (chips, badges, icons) | `back.out(1.7)` | 0.45–0.6 s |
| exits | `power2.in` | 0.25–0.4 s |
| ambient bob / drift | `sine.inOut`, yoyo, finite repeats | 1.2–10 s |

- Stagger lists 0.1–0.3 s; text words 0.28 s; characters 0.035 s.
- Text enters with y + blur (12px → 0) rather than plain fades.
- Transitions: circle iris (`clip-path: circle()`) for heroes, four colour blocks sweeping up for a
  topic change, video morph for layout changes. One primary transition style, max two accents.

## Sound

- Music bed −17 dB under the voice, sidechain-ducked, final mix −14 LUFS, true peak −1.5 dB.
- One SFX per visual event: `whoosh` = mode change / wipe, `hit` = hero lands, `pop` = chip/badge,
  `tick` = list item highlight + typing (every ~0.14 s at 0.35 gain), `rise` = bars/count-up, `ding` = payoff
  (answer, check, outro), `swoosh_soft` = small card in/out. Keep gains 0.4–1.0.
