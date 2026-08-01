# JSON Optional-Field TypeScript Ripple Effect — Worked Example

## Context

The App Centerpiece (`src/launcher-centerpiece/`) loads app definitions from `apps.registry.json`. Some apps have `"launch": null` (e.g., tradingview-api — it's URL-based, not launched locally). The original type required `launch: LaunchDefinition`, so parsing `null` crashed the whole registry.

## Change: Make `launch` and `stop` optional

### 1. Types file (`types.ts`)

```typescript
// Before
launch: LaunchDefinition;
stop: StopDefinition;

// After
launch?: LaunchDefinition;
stop?: StopDefinition;
```

### 2. Parser (`registry.ts`)

```typescript
// Before
launch: parseLaunch(input.launch, `apps[${index}].launch`),
stop: parseStop(input.stop, `apps[${index}].stop`),

// After
launch: isRecord(input.launch) ? parseLaunch(input.launch, `apps[${index}].launch`) : undefined,
stop: isRecord(input.stop) ? parseStop(input.stop, `apps[${index}].stop`) : undefined,
```

`isRecord()` checks `typeof value === "object" && value !== null`, so `null` cleanly resolves to `false`.

### 3. Process manager (`process-manager.ts`)

Every file that accesses `app.launch` needed a guard:

| Location | Before | After |
|----------|--------|-------|
| `buildPowerShellLaunchScript()` | `app.launch.env` | `if (!app.launch) throw new Error(...)` |
| `start()` | — | `if (!app.launch) return error status` |
| `stop()` | `app.stop.mode` | `if (!app.stop) return stopped status` |
| `refreshStatuses()` | `findMatchedProcess(app, ...)` | `if (!app.launch) { delete tracked; push default status; continue }` |
| `findMatchedProcess()` | `app.launch.startupProbe` | `app.launch?.startupProbe` |

### 4. Renderer (`renderer.ts`)

Hide Start/Stop buttons when launch/stop is undefined:

```typescript
// Before
<button class="action-button primary" data-action="start">Start</button>
<button class="action-button" data-action="stop">Stop</button>

// After
${app.launch ? `<button ... data-action="start">Start</button>` : ""}
${app.stop ? `<button ... data-action="stop">Stop</button>` : ""}
```

### 5. Tests

All access to `app.launch`, `app.stop` via optional chaining `?.` or non-null assertion `!`:

```typescript
// Optional chaining for access
assert.equal(cryptoRadar?.launch?.startupProbe?.mode, "processMatch");

// Non-null assertion inside type-narrowed scope
if (cryptoRadar?.launch?.startupProbe?.mode === "processMatch") {
  assert.equal(cryptoRadar.launch!.startupProbe!.match.field, "commandLine");
}
```

## General Rule

When making a type field optional:

1. **Parser** — Guard the value at parse time (`isRecord()` or `!= null`)
2. **Functions that use it** — Add early return/throw at the entry point
3. **Loops over entries** — Skip entries with undefined field
4. **Renderer** — Conditionally hide buttons/controls
5. **Tests** — Add `?.` or `!` assertions
6. **Build** — Confirm `tsc` compiles with zero errors
