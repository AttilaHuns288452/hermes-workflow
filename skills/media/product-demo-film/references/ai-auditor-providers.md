# AI auditor providers for video QA

Free, no-auth paths for independent video audits. Always cross-check every claim before editing (see SKILL.md QA step).

## OpenCode free models (text/code auditors)

`opencode run "<task>" --model opencode/<model>` — zero credentials needed; the free tier lists via `opencode models` (muse-spark-1.3-contributor-free, nemotron-3-ultra-free, mimo-v2.5-free and siblings). Work in a scratch dir containing the artifacts; the model can run Python/ffmpeg/ffprobe itself. Text-only: hand it structured data (timeline/cues JSON, frame file paths) and let it COMPUTE measurements (luminance scans, cue cross-reference checks) instead of describing images. One-shot `opencode run` needs no pty; budget ~2-5 min per run.

## xKiro vision models (visual auditors)

POST `https://api.xkiro.com/v1/chat/completions` with the XKIRO key from the Hermes `.env`, `content:[{type:'image_url', image_url:{url:'data:image/jpeg;base64,...'}},{type:'text',...}]`. Two hard requirements:

- Browser-like `User-Agent` header or Cloudflare rejects with 403 code 1010.
- Write the JSON body to a file and send `curl --data-binary @payload.json` — inline argv overflows the shell on multi-frame sheets.

Free plan-covered vision ids worth trying: `qwen/qwen3-vl-plus:free`, `qwen/qwen3.8-omni-flash:free`. Sheets of 6 frames at ~460px cells work well; ask for per-cell `label = OK | defect description` output to keep responses checkable.

## Triangulation expectation

Roughly half of free-model defect claims are false positives (bezel read as overflow, the PDF's own layout read as overlap, fast-seek phantom frames read as dark screens). The genuine catches — misaligned highlight rects, clipped text, wrong-element targets — more than justify the pass; verify each claim with word-box/pixel evidence, then fix only what survives.
