# Verifying a change is actually shipped (bundle-level proof)

When the claim is "the fix is live on the deployed site", not "the file changed". The deployment-status and deployed-suite steps live in `qa-suite-engineering` ("Deployed-claim verification"); this file covers the bundle-level proof mechanics:

- Fetch the live bundle with a cache-bust query (`?cb=<timestamp>`): CDN propagation and build-cache reuse mean a green deploy status is not a shipped change.
- Minified bundles erase code markers (component names, local identifiers). Use a surviving string literal from the change (a label, a URL, a class name) to locate the affected chunk, and check the marker in every lazily-loaded chunk that can contain the change — not just the entry chunk.
- Local `dist/` chunk names are not the production chunk names (separate builds hash differently). Extract the chunk names from the live entry bundle itself, then grep those.
- A complete bundle-level proof = a changed entry hash + a positive marker of the new code + the absence of the old marker where one existed.
- Pair the change's own targeted check with the journey/E2E suite against the deployed URL: the targeted check proves the fix landed, the suite proves nothing else broke. Both must pass against the deployed site, not the local build.
