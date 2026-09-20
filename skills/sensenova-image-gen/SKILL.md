---
name: sensenova-image-gen
description: Use when the user asks to generate an image. Free on xKiro.
---

# Free image generation via xKiro (SenseNova u1.5-lite)

## Endpoint (verified 2026-09-14)

Base: `https://api.xkiro.com/v1` — auth `Authorization: Bearer $XKIRO_API_KEY` (key in `~/.hermes/.env`).

It is an **async job API**, not synchronous like OpenAI:

1. POST — returns `{id, status:"processing"}`:
   ```bash
   curl -s https://api.xkiro.com/v1/images/generations \
     -H "Authorization: Bearer $XKIRO_API_KEY" -H "Content-Type: application/json" \
     -d '{"model":"sensenova/sensenova-u1.5-lite","prompt":"<prompt>","n":1}'
   ```
2. Poll the same URL + `/{id}` every ~5s until `status == "succeeded"` (~25s typical):
   ```bash
   curl -s https://api.xkiro.com/v1/images/generations/$ID -H "Authorization: Bearer $XKIRO_API_KEY"
   ```
3. Result: `data[0].url` → `https://cdn.xkiro.com/ai-image-generator/<id>/0.png` (public CDN).

Deliver with `MEDIA:` + local path after downloading from the CDN.

Default model `sensenova/sensenova-u1.5-lite` (free). For GPT-quality (better text rendering, up to 1312px) use model `gpt-image` — same POST/poll flow, ~$0.00963/image from wallet (verified 2026-09-14).

## Notes
- Model id is the full string `sensenova/sensenova-u1.5-lite` — no suffix.
- Prompt in English; describe subject, style, composition as usual.
- Chat models `sensenova/sensenova-6.8-flash-lite` and `-6.7-flash-lite` are also free (multimodal chat, 262K ctx) on `/v1/chat/completions` — optional free vision fallback if MiMo ever dies. Out of scope unless asked.
