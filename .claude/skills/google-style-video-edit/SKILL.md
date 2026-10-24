---
name: google-style-video-edit
description: Hassan's video editing style. Turns a raw talking-head phone video (Urdu / Hindi / English) into a clean, HD, Google-style animated short — silences and repeated takes cut, voice denoised, captions, soft Material motion graphics (video morphs into card / circle, search bars, chat bubbles, count-up bars, check + confetti), SFX and an original music bed — rendered with HyperFrames. Use whenever Hassan sends a video to edit, asks for "my style", "Google style", a short / reel, or a new video project in this repo.
---

# Google-style video edit (Hassan's style)

The pipeline scripts live in this repo (`scripts/`), the reusable composition in `template/`, and a
complete worked example in `examples/fsc-after-what-next/`. Read `references/style-guide.md` before designing
scenes and `references/scene-patterns.md` when you build them.

Talk to Hassan in plain English (he may write in Hindi / Urdu / Roman Urdu — answer in English unless he asks
otherwise). He is a creator, not a video engineer: explain choices in one line each, never dump tool output.

## The edit, step by step

0. **Setup (once per container):** `./setup.sh` — Whisper (sherpa-onnx, from GitHub releases because
   HuggingFace is blocked in cloud sessions), RNNoise, HyperFrames CLI, headless Chrome.
1. **Start the project:** `scripts/new.sh <raw.mp4> <name>` → creates `work/<name>/` and runs
   `transcribe.py` (silence-split chunks + English transcript, loudness per chunk).
2. **Pick what to drop** from `work/<name>/chunks.json`:
   - chunks below about -28 dB (mumbling, not talking to camera), `[static]` / `[Noise]`, anything under 0.4 s with no words
   - **repeated takes:** when a sentence is said twice, keep the complete/cleaner one and drop the false start
     (e.g. "If you are…" followed by "If you are a coder…" → drop the first)
   - never drop real content just to shorten; the short version is a separate cut.
3. **Cut:** `python3 scripts/cut.py <raw.mp4> work/<name> --drop 0,1,15` → denoised voice at -14 LUFS, every
   pause trimmed to ~0.12 s each side, 1080×1920 30 fps → `work/<name>/edited_HD.mp4`.
   Verify: re-transcribe a few windows of the output and check no word is clipped.
4. **Stage:** `scripts/stage.sh work/<name> projects/<name>` (template + footage with dense keyframes).
5. **Captions:** write `projects/<name>/captions.json` (chunk id → clean English caption, `[keywords]` in
   brackets get the brand colours) and `hide.json` for full-screen hero windows, then
   `python3 scripts/captions.py work/<name> projects/<name>`. It prints each chunk's time on the **edited**
   timeline — every animation time comes from that table.
   - Only caption what was actually said. If a phrase is unclear, leave it uncaptioned rather than guess.
   - Numbers on screen must match the audio exactly. If a number is ambiguous, re-run ASR on that window in
     several modes and, if still unsure, ask Hassan.
6. **Storyboard → scenes** in `projects/<name>/public/index.html` (see "Storyboarding" below).
7. **SFX cues** in `projects/<name>/sfx_events.json` — one cue per visual event (see style guide).
8. **QA before the long render:** `npx hyperframes lint projects/<name>/public` (0 errors) and
   `npx hyperframes snapshot projects/<name>/public --no-end --at <one time per scene>`; read the contact sheets
   and fix anything on the face, overlapping, clipped or unreadable. Zoom (`--zoom x,y,w,h`) on any Urdu/Arabic text.
9. **Render + mix:** `scripts/render.sh work/<name> projects/<name>` (~25 min per 2.5 min of video on 4 CPUs;
   run in the background, tell Hassan the estimate) → `final_with_music.mp4` + `final_no_music.mp4`.
10. **Deliver:** send both files, list what's in each section with timestamps, list the choices you made,
    and commit the project's source (not the mp4/wav files) back to the repo.

## Storyboarding

- One **section** per idea in the talk (hook → problem → advice → proof → payoff → outro). Pacing: something
  on screen changes every 2–4 s, a new layout every 10–20 s, and a full-screen hero card only at the 2–3 biggest
  lines (the "mantras"). Never more than one hero per ~30 s.
- Each section picks one **video mode**: `full` (face full-bleed, graphics in the lower band / sides),
  `card` (video morphs into a rounded top card, graphic panel below), `pip` (video becomes a circle with a
  spinning colour ring, content fills the canvas). Morph between modes, never cut.
- Build visuals from what the speaker *means*, not literal words: questions → search bar + suggestions;
  "AI understands your language" → chat bubbles → prompt → app assembling; a percentage → count-up bars;
  "yes" → drawn check + confetti; comparison → flip cards; list of skills → hub diagram.
- Keep the face visible except during hero cards. Overlays live in safe zones (see style guide).
- End with the outro card: four dots → the main mantra → one-line takeaway → "Follow for more".

## Lessons from past edits

- **Short reels (< 60 s):** one section per sentence or two, one hero only, outro may overlap the last spoken
  line (its text should repeat that line, e.g. "Let me know in the comments").
- An SVG path with a round linecap shows a dot before `drawPath` starts — keep it `opacity: 0` until the draw.
- The template already animates the background blobs; don't add a second blob tween in the scenes block.
- Ambiguous phrase (e.g. "if not then, when?"): caption what ASR consistently hears across modes and
  tell Hassan, so he can correct it.
- When waiting on a render, don't `pgrep -f render.sh` / `pkill -f` from a shell whose own command line
  contains that pattern — it matches itself. Check for the output file or use the background task notification.
- Render speed on 4 CPUs: ~13 s of wall time per second of video.

## Hard rules

- HyperFrames contract: one paused GSAP timeline at `window.__timelines["<composition-id>"]`; no
  `Math.random` / `Date.now` (seeded PRNG only); local fonts only; transforms/opacity over layout props;
  never tween visibility on `.clip` elements; `fromTo` with explicit start states.
- Music: no YouTube Audio Library or other external tracks are reachable from cloud sessions. Use
  `scripts/music.py` (original, no credit needed) and always also deliver the no-music version.
- No Google logo, wordmark or product names — "Google style" means the palette, the Material motion and
  the clean UI shapes only.
- Don't claim you listened to audio — you can only measure it (loudness, spectrum, re-transcription).
