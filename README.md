# Sun Video Editor Setup

Turn a raw talking-head phone video (Urdu / Hindi / English) into a clean, HD, animated short:
silences and false starts cut, voice denoised, captions, Google-style motion graphics made with
[HyperFrames](https://github.com/heygen-com/hyperframes), sound effects and an original music bed.

First video made with it: `examples/fsc-after-what-next` ("After FSC, what next?").

**Claude skill:** `.claude/skills/google-style-video-edit/` holds the full editing style (workflow, style guide,
scene patterns). Any Claude Code session opened on this repo picks it up — just send the raw video and say
"edit this in my style".

**New video:** `scripts/new.sh raw.mp4 my-video` creates `work/my-video/` + `projects/my-video/` and transcribes.

## Pipeline

| step | command | what it does |
| ---- | ------- | ------------ |
| 0 | `./setup.sh` | installs sherpa-onnx + offline Whisper medium, RNNoise model, HyperFrames CLI + headless Chrome |
| 1 | `scripts/new.sh raw.mp4 myvid` (runs `transcribe.py`) | splits at silences, transcribes each chunk → `work/myvid/chunks.json` (id, start, end, loudness, text) |
| 2 | `python3 scripts/cut.py raw.mp4 work/myvid --drop 0,1,15` | drops the chunk ids you list (noise, mumbles, false starts, repeated takes), denoises, cuts every pause, upscales to 1080×1920 → `edited_HD.mp4` |
| 3 | `scripts/stage.sh work/myvid projects/myvid` | new project from `template/`, footage staged with dense keyframes |
| 4 | write `projects/myvid/captions.json` (+ optional `hide.json`), then `python3 scripts/captions.py work/myvid projects/myvid` | timed caption groups → `public/captions.js`; also prints every chunk's time on the edited timeline |
| 5 | design scenes in `projects/myvid/public/index.html` and cues in `sfx_events.json` | the creative part — see below |
| 6 | `npx hyperframes snapshot projects/myvid/public --at 5,20,40` | check frames before the long render |
| 7 | `scripts/render.sh work/myvid projects/myvid` | lint, render (~25 min for 2.5 min of video on 4 CPUs), mix voice + ducked music + SFX → `final_with_music.mp4`, `final_no_music.mp4` |

### Choosing chunks to drop (step 2)

Look at `chunks.json`: drop chunks that are very quiet (`db` below about -28, i.e. not talking to camera),
pure noise (`[static]`, `[Noise]`), and the weaker take whenever a sentence is said twice
(keep the complete one, drop the false start).

### captions.json

Keys are chunk ids, values are the caption text for that chunk; wrap keywords in brackets to colour them:

```json
{ "7": "[What] [should] [I] [study]? What shouldn't I?", "8": "Should I go to [university] or not?" }
```

`hide.json` lists `[start, end]` windows (edited timeline) where a full-screen title card owns the screen and captions should hide.

### Scene building blocks (template/public/index.html)

- **Video modes:** `mode("full" | "card" | "pip", t, duration)` morphs the footage between full screen, a rounded top card, and a circle; `chrome("#card-shadow" | "#pip-ring", t0, t1)` fades the frame/ring in and out.
- **Helpers:** `layer`, `popIn`, `drawPath`, `typeText`, `blink`.
- **Look:** Material-style easing (`expo.out`, `power3.inOut`, `back.out(1.7)`), the four brand colours (`--blue --red --yellow --green`), soft blurred blobs behind the video.
- **Patterns in the example:**
  - search bar with suggestions
  - circle-iris title card
  - ripple hero
  - count-up bars
  - colour-block wipe
  - chat bubbles with Urdu/Balochi script
  - prompt → app assembling
  - check-mark + seeded confetti
  - flip comparison cards
  - skills diagram
  - outro

Rules HyperFrames enforces: one paused GSAP timeline registered as `window.__timelines["fsc"]`
(matches `data-composition-id`), no `Math.random`/`Date.now` (use a seeded PRNG), fonts only from local
files, animate transforms/opacity rather than layout.

### Audio

`scripts/music.py` synthesises an original lo-fi bed (C–G–Am–F, 88 BPM), so there is no copyright claim and no credit
is needed. `scripts/sfx.py` synthesises whoosh / pop / ding / hit / rise / tick / flash at the times in
`sfx_events.json` (`[[seconds, "kind", gain], ...]`). To use a YouTube Audio Library track instead, put it under
`final_no_music.mp4` in any editor and add the attribution the library asks for.

## Notes

- Captions are English (Whisper translate mode), because Urdu/Hindi script output from this model is unreliable.
- Caption timing is distributed across each chunk's duration (no word-level timestamps), good enough at 2–4 s chunks.
- The upscale from phone resolution sharpens the image, but it can't add real detail. Record at 1080p or higher when possible.

## Ideas for the next videos

- word-level caption timing (forced alignment)
- reusable scene sub-compositions (search, chat, bars…) so `index.html` stays small
- auto-suggest drop list (repeated sentences, quiet chunks)
- brand intro/outro sting
