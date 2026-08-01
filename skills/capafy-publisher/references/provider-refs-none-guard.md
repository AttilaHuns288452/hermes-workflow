# Provider Refs NoneType Guard

## Symptom

```
TypeError: 'NoneType' object is not iterable
```

Traceback chain:
```
packaging/configure/publish_configure.py:155  mode.configure(...)
  → packaging/configure/cloud_hosted/configure.py:85  build_staging_and_reviewed_scan(...)
    → cloud_hosted/pipeline.py:61  build_url_proxy_phase(...)
      → url_proxy/orchestrator.py:74  runtime.prepare(ctx)
        → hermes/url_proxy.py:50  ensure_hermes_official_providers(...)
          → hermes/auth_profile_materialize.py:29  _ensure_oauth_custom_providers(...)
            → hermes/auth_profile_materialize.py:89  find_custom_provider(...)
              → hermes/provider_refs.py:14  for provider in custom_providers:
TypeError: 'NoneType' object is not iterable
```

## Root Cause

`find_custom_provider(custom_providers, name)` in `packaging/configure/runtimes/hermes/provider_refs.py` assumes `custom_providers` is always a `list`, but it can be `None` when the Hermes `config.yaml` has no `custom_providers` key defined or sets it to `null`.

## Fix Applied

In `provider_refs.py`, `find_custom_provider()`:

```python
# Before (crashes when custom_providers is None):
def find_custom_provider(custom_providers: list[Any], name: object) -> Optional[dict[str, Any]]:
    normalized = _normalize_provider_name(name)
    if not normalized:
        return None
    for provider in custom_providers:  # TypeError here
        ...

# After:
def find_custom_provider(custom_providers: Optional[list[Any]], name: object) -> Optional[dict[str, Any]]:
    normalized = _normalize_provider_name(name)
    if not normalized:
        return None
    if not isinstance(custom_providers, list):
        return None
    for provider in custom_providers:
        ...
```

## Check if fix is already applied

```bash
grep -n "isinstance.*custom_providers" packaging/configure/runtimes/hermes/provider_refs.py
```

Should show line like `if not isinstance(custom_providers, list): return None` before the `for` loop.
