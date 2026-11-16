# Desktop model picker visibility (why models go "missing")

## The three surfaces

| Surface | What it lists |
|---|---|
| Composer model menu (`ModelCatalogMenu`, `apps/desktop/src/app/shell/model-catalog-menu.tsx`) | the **default-visible set** per provider (below); search spans every model regardless |
| `ModelPickerDialog` (`apps/desktop/src/components/model-picker.tsx`) | the row's full `models` list, verbatim |
| Edit Models dialog (`model-visibility-dialog.tsx`) | toggles that persist the user's visible set |

A "models are missing from the switcher" complaint is about the composer menu. The catalog
itself is rarely wrong — the menu intentionally shows a subset.

## Where the default-visible set comes from

`store/model-visibility.ts`, in order:

1. **User's stored set** (localStorage `hermes.desktop.visible-models`) — honored exactly once
   customized. Absent = defaults below.
2. **`featured_models`** from the provider row (backend: `hermes_cli/inventory.py::_apply_featured`)
   — non-empty list = the default-visible set, full stop.
3. **Top-N fallback** — first `DEFAULT_VISIBLE_PER_PROVIDER` (50) families in the row's `models`
   order. Row order for a discovered custom endpoint is the endpoint's own (arbitrary) order, so
   the cut is arbitrary: flagship models routinely fall outside it.

`_apply_featured` assigns: routing aggregators get a newest-per-lab shortlist, user-defined rows
feature their full catalog (local patch on this install, maintained by
`~/.hermes/scripts/ensure_agent_patches.py`), other rows empty. `is_user_defined` is the class to
reason about: a config `providers:` entry (custom endpoint), NOT a registry provider that merely
has a config block.

## Diagnosis procedure

Probe the exact payload the UI consumes, not the raw endpoint:

```bash
RP=$(ls -d ~/.hermes/tools/python-*/bin/python3 | head -1)
cd ~/.hermes/hermes-agent && PYTHONPATH=. "$RP" - <<'EOF'
import hermes_bootstrap  # dependency-path gate; without it imports fail on requests/ruamel
from hermes_cli.inventory import load_picker_context, build_model_options_payload
p = build_model_options_payload(load_picker_context(), explicit_only=True)
for row in p['providers']:
    print(row['slug'], len(row['models']), len(row.get('featured_models') or []))
EOF
```

Diff three layers to find where models are lost: the provider's live `/v1/models`,
`~/.hermes/provider_models_cache.json`, and the payload above. Layer 3 is what every picker
renders; layers 1-2 only explain it. A row can legitimately show fewer models than the endpoint
serves — check `featured_models` vs `models` before calling anything broken.

## The localStorage override and its caveats

Stored keys live in the Electron profile's Chromium storage
(`~/.config/<App>/Local Storage/leveldb`), keys `hermes.desktop.visible-models` and
`hermes.desktop.known-models`. Read presence with `strings <leveldb files> | grep -o 'visible-models'`
to learn whether the user curated; when they did, defaults no longer apply and the stored set is
the whole truth.

- A curated provider only auto-admits NEW models that land inside its default set — a model added
  past the cut stays hidden until the user re-opens Edit Models. Prefer fixing defaults in
  `_apply_featured` over seeding stored sets for this reason.
- Never write the leveldb from outside: a running Chromium owns and rewrites that store, so external
  edits are clobbered. Flip visibility through the Edit Models dialog.

## Pitfalls

- Backend payload changes need the desktop backend process restarted (the desktop spawns `hermes
  serve` at app launch and Python caches imports). Patching `hermes_cli/` never changes a running
  picker — say so instead of chasing the UI.
- `featured_models` is the backend's only knob over default visibility; `DEFAULT_VISIBLE_PER_PROVIDER`
  lives in frontend source and changing it needs a desktop rebuild. Prefer the backend knob.
- `drop_unofferable_model_ids` filters `models` and `featured_models` by the same rule after
  `_apply_featured` runs, so a featured list equal to the catalog stays consistent — no manual
  sync needed.
