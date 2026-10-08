# Parsing Facebook Messenger HTML exports

Export path: `~/your_facebook_activity/messages/inbox/<gc-name>_<id>/message_1.html`
(source: Facebook → Settings → Download your information → Messages → HTML).

## Two known formats — probe before writing the parser

- **Old format:** per-message blocks. Sender `class="_3-96 _2pio _16xh"`, time `_2lem`, body `_2let`.
- **New format:** one `<section class="_a6-g">` per message; sender in the `<h2>` heading; timestamp in `<div class="_a72d">`; body = everything between `<div class="_2ph_ _a6-p">` and `<footer>`.

**Print a structure sample around the first message body BEFORE writing the regex.** Blind regexes written against the guessed format return 0 matches and burn a round — inspect first, then parse.

## Parse recipe (execute_code)

1. New format: `re.split(r'<section class="_a6-g"', raw)[1:]`. Old format: per-message-div regex.
2. clean(): `<br>` → `\n`; `<img alt="X">` → `[emoji:X]`; `<div>` → `\n`; strip remaining tags; `html.unescape`; collapse repeated blank lines.
3. Filter sections without a timestamp (`time == "?"` — Participants / Group photo / invite-link headers).
4. Export is reverse-chronological (newest first) — reverse for timeline analysis.
5. Write `time | sender: body` lines to a workspace .txt and read it back in chunks. ~130 messages ≈ 55 KB — never rule on the first-screen preview.

## Gotchas

- Class attributes are multi-token: match the exact prefix, e.g. `<div class="_3-96 ([^"]*)"`, not the bare class token.
- Other members' reactions arrive as their own sections ("X reacted 👍 to your message") with otherwise-empty bodies. They are DATA: count them into the footprint inventory (warmth/support markers), do not discard as noise.
- "This message was unsent" entries: note the occurrence, do not reconstruct content.
- System events (nickname changes, pins, group naming, who-set-whose-nickname) are signal for authority/structure questions — they show who built the governance layer.
- Body regex spans nested divs: capture from the body-container open tag to the closing `<footer>`, then clean — do not try to match the exact inner div, nesting varies by message type (links, attached docs, polls).
