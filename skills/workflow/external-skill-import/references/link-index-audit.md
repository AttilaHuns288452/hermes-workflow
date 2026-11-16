# Auditing a curated link index ("awesome-*" lists) before integrating anything

A curated index is hundreds of links to other people's repos, not a tree you clone. The import procedure's tree-shaped steps do not apply. These are the steps that do, in order.

## 1. Measure the index itself first

```bash
curl -sL https://raw.githubusercontent.com/<owner>/<repo>/main/README.md -o /tmp/index.md
# entries are usually: - **[owner/name](url)** - description
grep -cE '^-\s+\*\*\[' /tmp/index.md
```

Parse them into `(name, url, description)` and compute four numbers before reading a single candidate:

| Number | How | What it tells you |
|---|---|---|
| Total entries | count | scale of the job |
| Duplicate rate | entry basename already a local skill dir or frontmatter `name` | how much re-sells what you own |
| Vendor share | entries from big-vendor orgs | how much is one product's SDK plumbing |
| Dead links | sample 30-40 with `curl -o /dev/null -w '%{http_code}' -L` | whether the list rots |

A healthy index can still be mostly useless: 1,279 entries from 402 owners, 24% vendor SDK guides, and only a handful of genuine coverage gaps. That is the normal shape. Do not let the entry count imply the work.

## 2. Resolve each shortlisted entry to a real repo

Redirector domains (`officialskills.sh`-style) and `tree/...` URLs hide the actual source. Resolve before planning:

```bash
gh api repos/<owner>/<repo> --jq '{full_name,stars:.stargazers_count,pushed:.pushed_at,license:.license.spdx_id,archived}'
```

Expect a meaningful share to 404. An entry whose repo does not exist is not a candidate, and chasing it wastes turns — record it and move on.

## 3. Gate on a proven capability gap, not on novelty

Bucket entries by the areas the user actually works in, then compare each bucket against the installed catalogue. The only actionable candidates sit in a bucket with real entries and zero local coverage.

Be explicit about the evidence for "zero coverage": a name grep is not enough. Check for the capability inside skill bodies too:

```bash
find ~/.hermes/skills -iname SKILL.md | xargs grep -il '<capability>' | head
```

## 4. Prefer MERGE into an existing custom skill over INSTALL

If the user has a hand-built skill for the domain, installing the vendor's version **shadows it** and loses local hard-won references. Extract only the specific traps the local copy lacks, add them as one `references/<topic>.md`, and wire it into the existing routing table.

To find those traps, probe the local skill for the mechanisms the candidate is known for (one grep per trap, count hits). A zero-hit trap is the only thing worth importing; everything else duplicates.

```bash
for pat in 'auth\.role\(\)' 'security_invoker' 'revoke execute' 'with check'; do
  printf '%-22s %s\n' "$pat" "$(grep -rciE "$pat" ~/.hermes/skills/<skill> | wc -l)"
done
```

All traps already covered means skip the install entirely. One genuinely missing trap out of ten means you import a paragraph, not the skill — in the Supabase case eleven traps were probed, ten already present, so the deliverable was a single `references/` file rather than a shadowing install.

## 5. Collapse families into one skill, never N rows

Upstream shipping 20 sibling topic skills for one domain is not a reason to add 20 catalogue rows. Every row costs ~19 tokens on every turn forever. Fold them into one SKILL.md with a routing table plus `references/<topic>.md` per topic: the cheap table always loads, the expensive depth only for the matching topic.

Drop the upstream siblings that exist to sell a paid service (cloud builds, hosted CI, org management). Those references never get read on a machine that builds locally.

## 6. Report the rejections with numbers

A decision table is the deliverable. For each rejected bucket, give the entry count and the local equivalent that made it redundant — that stops the same candidates being re-litigated next session. "Skipped 1,270 entries" is only credible with the duplicate/vendor/gap counts behind it.

## Pitfalls

- **Do not trust your own broad usage grep when deciding what to cut.** A `LIKE '%skill_view%'` scan over a messages table covers only rows matching the pattern and over-reports unused skills by an order of magnitude. Use `~/.hermes/skills/.usage.json` (`view_count`/`use_count`) as the authoritative source; skills under `external_dirs` have no telemetry at all, so a missing record means untracked, not unused.
- **A large advertised number is not a plan.** "85% of the catalogue is unused" from a bad scan would have disabled actively-used skills. Re-derive any cut list from telemetry before acting.
- **Do not add a retrieval layer to hold the catalogue.** CodeGraph does not index Markdown, and a search needs a query that already knows the answer. The passive catalogue row is what makes a skill discoverable at all.
- **Verify `tag`/`title` collisions in a claim before repeating it.** Several entries in these lists point at repos that do not exist under the advertised owner; confirm with `gh api` before citing a star count or a licence.
