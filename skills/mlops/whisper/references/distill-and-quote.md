# Distilling transcripts into reusable notes + verbatim quotes

Trigger: the user has a recording or transcript of an event (panel defense, critique, review, meeting) and wants notes that generalize beyond the presented project, or wants "exact words" of the speakers added.

## Procedure

1. Transcribe first (see the faster-whisper section in SKILL.md) or accept a provided transcript.
2. Split content: project-specific facts (strip) vs transferable lessons (keep). Generalize specifics to roles or classes — name the mechanism, not the product ("one cloud service", "the microcontroller", "a hazardous mechanism").
3. Organize by theme (architecture, security, UX, sustainability, presentation habits...), not by recording chronology.
4. For verbatim quotes: grep the transcript by keyword to locate segments, pull a contiguous window around each hit (e.g. `sed -n 'N,Mp'` on the line numbers grep returned), and quote the speaker exactly as transcribed with a `[MM:SS]` timestamp. Keep code-switched wording (Taglish stays Taglish). Trim stutters only lightly; mark `[audio unclear]` where ASR garbled a word instead of guessing.
5. Attach each quote as a blockquote under the lesson it supports (`> "..." [MM:SS]`), not in a separate appendix — the lesson + its evidence should read together.
6. Deliver as one markdown file in `~/Downloads`.

## Pitfalls

- A keyword grep returning zero hits means that content is NOT in this recording (it may come from another session the user also has notes on). Report the gap and keep those items paraphrased — never fabricate quotes or dress a paraphrase as a quote. The transcript is the only evidence.
- ASR splits sentences into one-word segments; reconstruct the sentence from consecutive segments and give it one timestamp window, not per-word timestamps.
- Never silently "clean up" a quote into better grammar — that turns evidence into paraphrase. Quote lightly trimmed ASR output as-is and note the transcription is verbatim-but-noisy.
- Project-specific proper nouns leak easily into generalized notes. Grep the deliverable for the source project's entity names before sending.
- Generalization is not vagueness: keep concrete quantities and limits ("532KB RAM", "half a month of time") — they are the reusable part.