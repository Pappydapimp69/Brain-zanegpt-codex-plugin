# Brain ZaneGPT

An installable Codex/ChatGPT plugin combining the complete ZaneGPT behavior skill with an offline Brain snapshot and persistent local mining.

## Dependencies

- Python 3.9 or newer (standard library only)
- Git is optional; `mine` uses it to summarize project evidence when available
- No API key, account connection, database, Node.js package, or network access is required at runtime

## Data and privacy

The bundled snapshot contains public, curated canon from the upstream Brain nodes. It excludes Git history, incoming queues, sandboxes, credentials, local `.brain` data, and raw conversations. User-mined knowledge is stored outside the plugin and survives reinstall or upgrade. There is no automatic remote sync.

Run `python scripts/brain.py status` to see the exact local data directory. Override it with `BRAIN_ZANEGPT_DATA`.

## CLI

```text
python scripts/brain.py status
python scripts/brain.py query reachability
python scripts/brain.py query reachability --verbose
python scripts/brain.py mine
python scripts/brain.py mine --add proposal.json
python scripts/brain.py sync
python scripts/brain.py export --out brain-local-export.json
python scripts/brain.py sync --import brain-local-export.json
```

`sync` is deliberately local-only. It validates and promotes staged proposals, or imports an explicitly named local export. It never contacts GitHub or another remote.

## Sources

- <https://github.com/Pappydapimp69/Brain>
- <https://github.com/Pappydapimp69/Zanegpt>
- Public Brain nodes listed in `snapshot/MANIFEST.json`

See `THIRD_PARTY_NOTICES.md` before redistribution.
