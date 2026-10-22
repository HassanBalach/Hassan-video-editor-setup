# Hassan video editor setup

This repo turns Hassan's raw talking-head videos into Google-style animated shorts.

- For any video edit request, follow the skill `.claude/skills/google-style-video-edit/SKILL.md`.
- Start every new video with `scripts/new.sh <raw.mp4> <name>`; work files go to `work/<name>/`, the editable
  project to `projects/<name>/`.
- Commit project sources (captions.json, sfx_events.json, public/index.html, captions.js). Never commit video,
  audio, models or node_modules (see `.gitignore`).
- Reply to Hassan in English, short and plain.
