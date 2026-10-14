---
name: explainer-video
description: Builds short, direct English explainer videos (slides + synthetic voice-over + SRT) from a PDF or doc. Use when asked for a YouTube/explainer video of a document.
---
# Explainer video (direct style)

Output: `video/<name>.mp4` (1080p), `.srt`, `narration_<name>.txt`. Offline: Pillow + Kokoro TTS + ffmpeg.

## Style rules (non-negotiable)
1. **Hook in 5 seconds.** Slide 1 shows the single result or idea that makes the viewer think "that's what I wanted" (a big number pair or a one-line diagram). No intro, no "welcome".
2. **Order: WHAT, then HOW, then WHY.** WHAT = the result or the nail (1-2 slides). HOW = concrete steps, commands, numbers (the bulk). WHY = the reasons and caveats, last. Tag each slide `WHAT`/`HOW`/`WHY` (Italian: `COSA`/`COME`/`PERCHÉ`) as the first word of its title.
3. **Direct voice.** Short sentences, no corporate words, no recap of what the doc is. Numbers written as words in narration (TTS reads them better).
4. **Faithful.** Every figure comes from the source. Label estimates as estimates; state the caveats on a slide near the end.
5. 3-4 minutes. One idea per slide, max ~6 lines of text.

## Workflow
1. Read the source (`pdftotext -layout`). Pick the core; draft slides in WHAT/HOW/WHY order.
2. Write a spec JSON (see `specs/scaffold-antigravity.json`).
3. `python3 .claude/skills/explainer-video/build_video.py specs/<spec>.json --out video` (first run downloads the Kokoro model, ~350 MB, from GitHub releases; override dir with `KOKORO_DIR`).
4. Check 3-4 slides visually (montage + Read), commit, push, send the mp4 to the user.

## Spec format
`{"name","footer","voice":"af_heart","lang":"en-us","legend":["baseline","optimised"],"speed":1.05,"slides":[{"title","kind","content","narration"}]}`
Kinds and `content`:
- `hook`: `{"top":[line1,line2],"left":[big,sub],"mid":[big,sub],"right":[big,sub],"bottom":text}`
- `bullets`: list of strings (`""` = gap)
- `code`: list of lines (lines starting with `#` are muted)
- `table`: list of rows, first row is the header
- `bars`: list of `[label, baseline_text, optimised_text, baseline_value, optimised_value, diff_text]`
- `steps`: list of `[number, headline, detail, chip_text]`
Italian: `"lang":"it","voice":"if_sara"` (or `im_nicola`); write numbers as Italian words in `narration` (e.g. 107.103 -> centosettemilacentotré). Specs: `scaffold-antigravity.json` (EN), `*-it.json` (IT).
Deps: `pip install pillow kokoro-onnx soundfile numpy`; needs `ffmpeg`.
