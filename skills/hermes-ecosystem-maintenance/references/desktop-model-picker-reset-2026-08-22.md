# Desktop Model Picker: "Defaulting to wrong model" investigation

## Symptom
User selects a model (e.g. `meta/muse-spark-1.2-contributor`) in the desktop picker, but the UI keeps showing `xiaomi/mimo-v2.5` instead. `config.yaml` is confirmed correct (`model.default: meta/muse-spark-1.2-contributor`, `model.provider: opencode-go`).

## Root causes (two independent triggers)

### 1. localStorage visibility cache (`hermes.desktop.visible-models`)
The desktop model picker has a **visibility filter** separate from the config default. Stored in Electron's localStorage under key `hermes.desktop.visible-models`. This is a JSON array of `provider::model` keys.

- If a user toggled OFF `muse-spark-1.2-contributor` in Edit Models, it gets removed from the visible set.
- The picker then shows the next visible model (often `mimo-v2.5` which is near the top of opencode-go's list).
- This is NOT the config default — it's a UI curation layer.

**Fix:** Open Edit Models → re-enable the model. Or clear localStorage:
```js
localStorage.removeItem('hermes.desktop.visible-models')
```

**Source:** `apps/desktop/src/store/model-visibility.ts`
- `DEFAULT_VISIBLE_PER_PROVIDER = 50` (curated top-N fallback)
- `effectiveVisibleKeys()` resolves stored keys + defaults for un-customized providers
- `expandProviderDefaults()` uses `featured_models` shortlist when available, else top-N families

### 2. Fallback chain 429 response
`fallback_providers` in config.yaml can cause the UI to briefly show the fallback model that actually answered when the primary 429s. On opencode-go, Muse Spark can 429 transiently.

**Fix:** Not a config issue — just retry. The fallback chain (config line 102-108) has mimo as 3rd entry, which is what shows during the 429 window.

## Config verification (always check first)
```bash
hermes config get model.default   # should show the intended model
hermes config get model.provider  # should show the intended provider
hermes config get fallback_providers | head -n 10
```

## Desktop model picker architecture
The flow is: `config.yaml model.default` → backend `/api/model/info` → desktop `$currentModel` store → composer display. The **visibility filter** (`effectiveVisibleKeys`) is separate and comes from localStorage, gating which models appear in the dropdown regardless of what the config says.

Key files:
- `apps/desktop/src/store/model-visibility.ts` — visibility set persistence
- `apps/desktop/src/app/session/hooks/use-model-controls.ts` — model selection/seeding logic
- `apps/desktop/src/app/shell/model-catalog-menu.tsx` — the picker dropdown UI
- `gateway/platforms/api_server.py:2788-2926` — server-side model resolution chain
