# Vetting a site/provider for legitimacy (scam triage)

Compact recipe, proven 2026-08-19 on 1024EX (an "AI trading platform" promoted via
Instagram reels + one r/defi post). Use when the user asks "is <site> legit?" — a
common question for a finance-focused user pitched crypto/trading/broker platforms.

## The recipe (5 parallel-ish probes, then verdict)

1. **Domain age + registrar (RDAP, no whois needed):**
   `curl -s "https://rdap.verisign.com/com/v1/domain/<domain>"` → `events[].registration`
   gives creation date. A site < ~1–2 years old + cheap registrar (Name.com) = weak trust anchor.
   Companies are a single check away; anonymity + recency is a red flag, not proof.
2. **Independent presence:** search `<name> reviews`, `<name> scam`, `<name> warning`.
   Look for r/CryptoScams, r/Scams, regulator advisories (FINRA/CFTC/RCMP/scamwatch.gov.au).
3. **Astroturf detector:** social-media reels + a lone Reddit "tried 3 bots, this one
   seems legit" post = classic fabricated-promotion pattern. The promotion channel is
   part of the verdict, not noise. A single positive self-report is not evidence.
4. **Regulatory/license hunt:** real exchanges holding customer funds publish a legal
   entity, jurisdiction, and license (MSB/VASP/CTF registration). If a search for
   "<name> license|registered|company" turns up ONLY licensing-services adverts → no license.
5. **Product verifiability:** "paper demo only" / "sign in to see live" front doors mean
   there's nothing independently verifiable. Note what's behind the paywall/sign-in.

## Verdict language (be honest, don't overclaim)

- "No confirmed victim reports naming it" ≠ "legit". Say exactly that.
- Verdict tiers: confirmed scam (reports/regulator) / high-risk-likely-scam (young domain,
  no license, no legal entity, astroturf marketing) / no-evidence-either-way / legit.
- Give the specific red flags you found as a table, and a concrete "don't deposit real
  money; if pushed via a friend/Telegram/signals group it's probably a pump-and-withdrawal-block."

## Variant: it's not a scam, it's just a new tool/company

Same recipe kills false positives: a young domain alone is not damning if the company
has a real legal entity, staff, a working product, and neutral third-party coverage.
