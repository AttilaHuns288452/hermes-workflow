---
name: study-tools
description: Use when Attila asks for a reviewer, quiz, or study app.
category: education
---

# Study Tools — reviewer + quiz app from course material

## Standing preferences (every build, whole rules)

- Deliver BOTH artifacts: `<Course>_Reviewer.md` (printable contract) and `<Course>_Study.html` (single-file drill app, no build step, works over file://).
- The quiz must cover EVERY definition and EVERY enumeration in the material — both MC items and type-the-answer enumeration items.
- Sub-quiz at the BOTTOM of each topic page (that topic's items only) plus a Master Quiz (all items) on the quiz tab.
- Mistake loop: wrong answer → immediately show the correct answer + explanation → results screen lists every miss with the correct answer → "Redo Mistakes" re-runs only the misses, reshuffled → repeat until 100%. Persist lifetime miss counts in localStorage and resurface weakest items in later sessions.
- No advancing until the current question is answered: MC click = select only, Submit = evaluate, Next stays disabled until evaluated.
- Visualizations tab with SVG trees/graphs for hierarchical material (phase chains, matrices, taxonomies) — he asks to "visualize more fully".
- Every tabbed HTML reviewer ships an **index tab** (first content tab, right under Overview) listing ALL topics on one screen as cards: live visual preview per topic, complexity badge, group filter chips with counts, a search box, and click-through into that topic's tab. Theory-only topics get a mono math glyph as their preview.
- Plain English, dark theme, keyboard shortcuts (1-4 select, Enter submit, arrows navigate).

## Extending an existing reviewer HTML ("improve this, add a tab")

Before writing anything, extract the page's OWN machinery — the fastest correct build reuses it instead of importing parallel CSS/JS:

1. **Map structure first** (one regex pass, not read_file of the whole file): tab ids (`pane-*` / `data-tab`), nav link format, shared helpers (`drawGraph`, `wireStepper`, `el`), which SVGs draw at init vs behind a button, and CSS hook classes. Complexity formulas live in `<span class="formula">…</span>` inside each pane — copy them from there verbatim so the index never contradicts the body.
2. **Reuse the page's graph data, don't redraw.** Thumbnails that call the page's own `drawGraph()` with the module's exact nodes/edges/viewBox match the walkthroughs 1:1. Extract JS array literals to JSON by quoting unquoted keys (`re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', …)`) AND stripping trailing commas (`re.sub(r',\s*([\]}])', r'\1', …)`) — json.loads fails on both.
3. **Inject additively:** CSS before `</style>` (assert count==1), nav link after Overview, section before the next module comment, and the new `<script>` IIFE appended after the LAST existing `</script>` — never inside the original script block. Cards navigate by calling `.click()` on the existing nav link, so tab routing stays single-sourced.
4. **Same verification gate as a fresh build** (step 6 above): node --check every script block, then a playwright smoke over file:// that opens the new tab, exercises search/filter/click-through, revisits an old tab, and asserts zero pageerrors. Add a pixel check (sample for the theme's accent colors in the screenshot) — a functionally-passing page can still render blank thumbnails.


## Pipeline

1. **Extract deck content.** Try read_file; if it errors "no extractable text", the deck is image-only slides (screenshot export) — do NOT retry read_file, go to step 2. `python-pptx` may be absent; stdlib handles everything.
2. **Extract slide images in order:** `python3 <this skill>/scripts/extract_pptx_media.py deck.pptx outdir/` — stdlib zipfile + slide rels. Image-only detection: slide XML containing no `<a:t>` runs.
3. **Transcribe slide images with the native vision API** → follow references/vision-transcription.md exactly (batched, checkpointed per deck, background process).
4. **Author the question bank as Python data modules** (`quizdata_a.py`, `quizdata_b.py`, …): MC items `{t:'mc', q, a, w:[3 wrongs], x, topic}` and enum items `{t:'enum', q, parts, o, x, topic}` where `parts` is a list of accepted-answer lists and `o` marks ordered enumerations. Balance MC answer placement:
   ```python
   pos = Counter()
   for it in mc_items:
       target = min(range(4), key=lambda p: pos[p])
       it['opts'] = ...correct at target, wrongs elsewhere...
       it['ans'] = target; pos[target] += 1
   ```
   Coverage check: every definition ≥1 question, every enumeration 1 enum item + MCs for its members; print per-topic counts.
5. **Build:** a Python script imports the data modules, balances, and injects into `templates/study_shell.html` by replacing the bare tokens `__TOPICS__`, `__QUIZ__`, `__REVIEWER__` (json.dumps, ensure_ascii=False, separators to shrink).
6. **Verify — mandatory, an unverified build ships blank:**
   a. Extract the `<script>` body to a file → `node --check` (catches injection syntax errors instantly).
   b. Headless playwright smoke (`NODE_PATH=/home/attila/.hermes/hermes-agent/node_modules`): launch over file:// → open quiz tab → start → select → submit → assert Next unlocks → reach results → redo mistakes → start a sub-quiz → assert zero pageerrors throughout.
7. **Deliver** with MEDIA: plus a 3-line "how the loop works" note.

## Pitfalls

- **One `<script>` block means one syntax error blanks the ENTIRE app.** The user reports "I don't see the quiz", never an error message. Classic cause: injecting JSON with `.replace()` over a line that keeps a trailing literal — `const ITEMS = /*x*/[];` + replacing `/*x*/` yields `…][]`. Keep template tokens as bare statements (`const ITEMS = __QUIZ__;`) so the token replaces the default value wholesale, and run node --check after every build.
- **Flatten accepted-answer arrays at the point of use:** `const accepted = (answers[i]||[]).flat();` in BOTH the enum checker and the results/answer display. Nested parts arrays survive json.dumps and then throw `a.toLowerCase is not a function` mid-quiz.
- **Click-to-answer defeats the gate.** If clicking an option evaluates immediately, users skip feedback and the mistake loop never fills. Select highlights, Submit evaluates.
- **Score results off `Object.values(marked)`, and map mistakes to session positions by id** (`session.findIndex(s => s.id === id)`) — index-based lookups break after reshuffles and report wrong "your answer" lines.
- **Increment the mistake bank only on wrong answers:** `mastered[id] = (mastered[id]||0) + 1` inside the wrong branch, then persist.
- **Long vision batches must run as a background terminal process,** not inside execute_code — the kernel is killed at the timeout and the loop with it; JSON checkpoints on disk survive and a rerun fills only the gaps.
