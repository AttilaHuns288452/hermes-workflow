# Anime Waifu Quiz - image audit 2026-08-19

## Totals
- `lib/characters.ts` 427 blocks, originally `imageUrl:` 219, missing 208
- After `scripts/fetched_missing.json` (208 fetched) patched -> 427, then reverted 2 fakes -> **425 real + 2 fallback** (100% distinct per name)

## Fetch session
- Script `C:/tmp/fetch_missing.py` - AniList GraphQL `Page(perPage:8){characters(search:$search){id name{full} image{large}}}`
- Rate ~0.8s, retry 429 with 8-10s wait. Scored via `SequenceMatcher` + `a in b` 0.92 boost, cleaned name `\(.*?\)` strip.
- Variants: cleaned, first-token, first-two-words. Accept >=0.4, LOW <0.65 for manual.

## LOW 13 flagged (same-person reversals are OK)
- `boa-hancock` 0.64 Hancock Boa - same id 16342, keep
- `saber-artoria` 0.55 Altera - WRONG, fixed to Artoria Pendragon b497
- `senjougahara-hitagi` 0.63 Hitagi Senjougahara - same id b22037, keep (reverse)
- `nel-tu` 0.60 Enel - WRONG, fixed to Nelliel b4730
- `roronoa-zoro` 0.58 Zoro Roronoa - same id b62, keep
- `monkey-d-luffy` 0.44 Luffy Monkey - same id b40, keep
- `okabe-rintarou` 0.57 Rintarou Okabe - same id b35252, keep
- `aizawa-shota` 0.52 Tomo Aizawa - WRONG, fixed to Shouta Aizawa b89225
- `portgas-d-ace` 0.56 Ace Portgas - same id b2072, keep
- `ainz-ooal-gown` 0.46 Cains Rackin - WRONG, fixed to Momonga b89103
- `dr-tenma` 0.61 Umatarou Tenma - WRONG, fixed to Kenzou Tenma b718
- `might-guy` 0.56 Guy Might - same id b307, keep
- `tohno-shiki` 0.45 Shiki Tohno - same id b2212, keep

Manual alias fixes applied: `sesshomaru` -> Sesshoumaru b1358 (romanization), `all-might` -> Toshinori Yagi b89224, `hawks` -> Keigo Takami b128299, `lunge` -> Heinrich Runge b721, `nel-tu` -> b4730.

## Dups after
10 dups remain, all intentional same-person: `yor-forger`+`yor-forger-already`, `shoko-komi`+`komi-shouko`, `jolyne-kujo`+`jolyne-fn-kujo`, `tanjiro-kamado`+`tanjirou-already`, `lelouch-vi-britannia`+`lelouch-already`, `roy-mustang`+`roy-mustang-already`, `traflagar-law`+`trafalgar-law`, `ken-kaneki`+`sasaki-haise`, `thorfinn`+`thorfinn-karlsefni`, `cid-kagenou`+`shadow-cid-alter`. 

Fake 2: `anri-yoshioka` + `ryo-mukohara` (Romantic Killer invented names) have no AniList hit; anime cover `bx153930` was removed so fallback `DiceBear?seed=name` gives distinct per-name image.

## Verify
`npx next build` - 438 pages, 4.1s compile, 6.6s generate, ok.

## Follow-ups
- Recipe to extend: add missing future characters via same fetch script; re-run audit.
- Ponytail fallback: `getCharacterImage(name, url?)` one-liner, no object wrapper.
