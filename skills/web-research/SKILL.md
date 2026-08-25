---
name: web-research
description: "Use for multi-source web research and cited reports."
version: 1.0.0
metadata:
  hermes:
    tags: [Research, Web, Retrieval, Citations, Reports]
    category: research
---

# Web Research (retrieval operations)

Use when producing any multi-source web research deliverable — competitive/product research rounds, cited reports, market scans — on this host's search/extract stack. Covers the *retrieval* half: pacing under shared quotas, extracting without burning quota, fallbacks for blocked sites, and reading fetched pages locally. For citation mechanics (ledger, evidence quotes, Sources blocks) see the external `grounded-citations` skill — this skill defers to it; the two do not overlap.

## Core rule: the search/extract backend is a SHARED per-minute quota

On this host, `web_search` and `web_extract` (Firecrawl backend) share one per-minute request quota (~13 req/min) across ALL parallel agents. Symptoms and handling:

1. **Parallel batches exhaust the quota instantly.** 4 batched searches = the whole minute gone (`Rate Limit Exceeded ... Consumed (req/min): 13, Remaining: 0`). Do NOT fire more than ~2 calls per minute; when multiple agents run in parallel, assume even less.
2. **Rate-limit responses can be SILENT.** In `execute_code`, the `web_search` helper may return `{"data": {"web": []}}` with no error when quota is exhausted — an empty list that looks like "no results." **Retry on empty, not just on exceptions.** The rate-limit error only surfaces through the direct tool call.
3. **Paced loop pattern that works** (use in `execute_code` to keep context lean): for each query, loop up to N attempts: call → if results non-empty, print compact (`title | url` + first ~180 chars of description) and break; on exception OR empty, sleep 12–20s and retry; sleep ~8–10s between queries. 5–8 queries fit in a 5-min script; if some fail, finish them as direct tool calls after the quota resets.
4. **Extraction shares the same quota** — batch `web_extract` (max 5 URLs/call) only when headroom is known; otherwise extract 1–2 URLs per call with sleeps, and set `char_limit` (6000–9000) so you get head+tail without bloating context.

## Read the middle from disk, don't re-fetch

`web_extract` on pages over the char budget saves the FULL text locally and prints a footer with the path: `C:\Users\Attila\AppData\Local\hermes\cache\web\<domain>-<hash>.md` (on Windows, `$LOCALAPPDATA/hermes/cache/web/`). When you need the omitted middle: `read_file <path>` at the printed offset, or `terminal` `grep -in "<keyword>" <path>` to pull just the relevant section. **This costs zero quota and avoids a second fetch.** The cache dir is shared with sibling agents — other files there are not yours; only trust the path printed in your own tool output.

## Blocked-site fallbacks

Some sites refuse scraping (`Website Not Supported` — Investopedia, Reddit) or are flaky. Patterns that work:

- Reddit: try `old.reddit.com` URL — often still blocked; the search-result snippet alone supports only what it literally says.
- Paywalled/blocked article: cite the search snippet's claim with the URL, and corroborate the same fact from an extractable secondary source (e.g., NPR affiliates syndicate wire stories; vendor blogs restate surveys). One source reporting + one corroborating = defensible; say which you read fully.
- Search descriptions can carry the whole claim (`"1 in 5 Americans lost more than $100..."`) — usable as a snippet-level citation, but flag it as such rather than quoting the page body.

## Deliverable format (this user's research rounds)

- Structured markdown, ~800–1200 words for strategy briefs, URLs **inline** as markdown links (parent/task often specifies this — obey the task over the ledger style), one Sources section if requested.
- Ground every load-bearing number to the page you actually read (quote figures as the source states them); mark model-knowledge claims `[unverified]` rather than inventing a citation.
- When the research feeds a product repo (e.g., CashFlow OS), the round's condensed findings + URLs get saved under that skill's `references/` with a one-line pointer in its SKILL.md — that is the convention for this user's research rounds.

## Delivering results to Attila

- **Markdown tables in chat** — present price/product listings as markdown tables directly in the conversation, not as code files. User explicitly prefers seeing the data in chat over receiving a file to open.
- **Use his currency** — Attila uses Philippine pesos (₱). Convert USD prices to PHP (check current rate) and show both. Default to pesos in the primary column.
- **Run code, don't paste it** — if asked to "convert to X" (language, format), write the file AND run it, don't just show code blocks for the user to copy.
- **Flag suspicious data** — prices far below market floor (e.g. $480 for a $790+ card) should be called out as likely scams, not presented as valid options. If a listing came from a search snippet (not a verified page), say so.
- **"Is <site> legit?" vetting** — use `references/vetting-suspicious-sites.md` (RDAP domain age, license/regulatory hunt, astroturf detector, verdict language).

## Pitfalls

- Don't retype URLs into a report from memory — only URLs that appeared in tool output (search results or extraction footers).
- A search snippet supports only what it literally says; if the claim needs the body, `web_extract` it first (see grounded-citations for the same rule on quotes).
- Don't treat the first rate-limit failure as fatal — the quota resets within a minute; the retry loop is the fix, not a different tool.
