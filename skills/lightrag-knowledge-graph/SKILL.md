---
name: lightrag-knowledge-graph
description: Query the local skill knowledge graph semantically.
---

# LightRAG Knowledge Graph

Local LightRAG (HKUDS) server that indexes every `SKILL.md` into an entity/relation
graph. Use it for **semantic, cross-skill** questions. For exact name lookup use
`lightrag_find.py` (BM25, instant); for reading a specific skill use `skill_view`.

## Service

| | |
|---|---|
| URL | `http://127.0.0.1:9621` |
| API key | `lr_local_hermes_9621` (header `X-API-Key`) |
| Unit | `systemctl --user status/restart lightrag.service` |
| WebUI | `http://127.0.0.1:9621/webui` |
| Data | `~/.hermes/lightrag_db/` (JsonKV + NanoVectorDB + NetworkX) |
| Repo | `~/Documents/Projects/lightrag` (venv `.venv`, v1.5.8) |
| LLM | xKiro `mistralai/mistral-medium-3.5` (plan-covered) |
| Embedding | local Ollama `nomic-embed-text` (768d) |

## CLI

```bash
python3 ~/.hermes/scripts/lightrag_hermes.py status
python3 ~/.hermes/scripts/lightrag_hermes.py ask "question" [--mode mix|local|global|hybrid|naive]
python3 ~/.hermes/scripts/lightrag_hermes.py index-skills          # incremental sync
python3 ~/.hermes/scripts/lightrag_hermes.py index-skills --reset  # rebuild
python3 ~/.hermes/scripts/lightrag_hermes.py index-skills --with-references   # +2,751 files, hours
python3 ~/.hermes/scripts/lightrag_hermes.py graph "CONCEPT"
```

Reindex in the background (survives the agent's memory cgroup):

```bash
systemd-run --user --collect --unit=lightrag-index --setenv=PYTHONPATH= \
  bash -lc '~/Documents/Projects/lightrag/.venv/bin/python ~/.hermes/scripts/lightrag_hermes.py index-skills'
journalctl --user -u lightrag-index -f
```

Query modes: `local` (entity-centric), `global` (theme/relation-centric), `hybrid`,
`naive` (plain vector), `mix` (default, graph + vector).

## Raw API

```bash
curl -s -H 'X-API-Key: lr_local_hermes_9621' -H 'Content-Type: application/json' \
  -d '{"query":"...","mode":"mix"}' http://127.0.0.1:9621/query

curl -s -X POST -H 'X-API-Key: lr_local_hermes_9621' -H 'Content-Type: application/json' \
  -d '{"text":"...","file_source":"mydoc.md"}' http://127.0.0.1:9621/documents/text

curl -s -H 'X-API-Key: lr_local_hermes_9621' http://127.0.0.1:9621/documents/pipeline_status
curl -s -X POST -H 'X-API-Key: lr_local_hermes_9621' -H 'Content-Type: application/json' \
  -d '{"limit":10,"page":1}' http://127.0.0.1:9621/documents/paginated
```

## Pitfalls

- **`file_source` is reduced to a basename** and is the document identity. Two
  files both called `SKILL.md` collapse into one doc. Always send unique flat
  names (`skills__decide.md`). `/` and `:` are rejected outright.
- **`PYTHONPATH` must be empty** when starting the server. This shell exports a
  Python 3.14 site-packages dir that shadows the venv's pydantic and crashes
  startup with `ImportError: cannot import name 'ArgsKwargs'`. The systemd unit
  sets `Environment=PYTHONPATH=`.
- **Chunking payload**: `{"strategy":"fixed_token","params":{"chunk_token_size":900,
  "chunk_overlap_token_size":100}}`. Wrong keys → HTTP 422 at request parse time.
- **Embeddings are local-only.** No provider in `config.yaml` serves
  `/v1/embeddings` (xKiro/stdcmpt/commandcode all 404). Do not try to point
  `EMBEDDING_BINDING_HOST` at a chat gateway.
- **Delete/clear waits on the pipeline.** `DELETE /documents` returns
  `{"status":"busy"}` while ingesting; poll `/documents/pipeline_status` for
  `busy:false` first.
- **Chat-model choice matters for extraction.** DeepSeek routes are PAYG-only
  (403) on xKiro; the plan-covered Mistral models work until the **daily
  free-model token quota** is spent, after which every xKiro free model answers
  429 `You've reached today's free-model token quota`. Switch the LLM block in
  `.env` to CommandCode `deepseek/deepseek-v4.1-flash` (host
  `https://api.commandcode.ai/provider/v1`) and restart — it emits clean JSON and
  is not on that quota.
- **A quota wall mid-run leaves documents `failed`.** Fix with
  `POST /documents/reprocess_failed` (one retry per failed doc per request), or
  `python3 ~/.hermes/scripts/lightrag_retry_failed.py`, which re-derives each
  file from its `file_source` and resubmits it. Both eventually reach
  `failed: 0`.
- Indexing throughput ≈7 docs/min; full 573-skill corpus ≈70 min. Don't run it
  in the foreground of a turn.
- Server RSS settles around 1.3 GB for a 32k-node graph; storage on disk ≈650 MB
  (the LLM response cache is most of it — drop `ENABLE_LLM_CACHE` only if disk
  matters more than re-extraction speed).
- `pkill -f lightrag-server` kills the invoking shell too (pattern in its own
  argv). Use `pkill -f '[l]ightrag-server'` or `systemctl --user restart`.
- Indexing throughput ≈7 docs/min; full 573-skill corpus ≈80 min. Don't run it
  in the foreground of a turn.

## Cost

Extraction is the only spend. xKiro plan coverage is free but quota-capped per
model tier; CommandCode DeepSeek is cheap and uncapped for this volume.
Embeddings are local via Ollama (nomic-embed-text, CPU).

## Corpus coverage

Default corpus = `~/.hermes/skills` (573 SKILL.md → 32k graph nodes, 44k edges).
`--with-references` adds `~/Documents/SkillReferences` (2,751 more files) —
budget hours and check the LLM quota first.
