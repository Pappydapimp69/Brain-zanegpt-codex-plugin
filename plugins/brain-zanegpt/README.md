# Brain ZaneGPT

An installable Codex/ChatGPT plugin combining the complete ZaneGPT behavior skill with Brain's canon, Brain's own CLI and the memory repo's own steward, all running offline. Lessons a user mines locally pass the same gate, reviews and training as the shared Brain canon.

## Dependencies

- Python 3.9 or newer (standard library only)
- Git is optional; `mine` uses it to summarize project evidence when available
- `check` (the ZaneGPT check on trial picks) uses `claude -p` or `codex exec` as a separate agent when either is installed; otherwise it prints the prompt and takes `--answer <file>`
- No API key, account connection, database, Node.js package, or network access is required otherwise

## How local lessons are held to the shared bar

- **Same gate.** `sync` runs the memory repo's `scripts/steward.py` unmodified: schema, substance, provenance, injection scan, dedup against shared and local canon, Composed references, sandbox checks, and the ZaneGPT check on trial picks. Its `cited_by.py` and `validate.py` follow-ups run too.
- **Same reviews and tiers.** Audits and rebuilds of local lessons (and of shared ones) are filed as reviews and applied by the steward. Tiers come only from those steward lines.
- **Same training and analysis.** `train`, `challenge`, `paths`, `analyze`, `tension` and `scorecard` are Brain's own commands and treat local lessons as canon.
- **Append-only.** A sync that would remove a local entry is refused.

Local lessons file into `projects/<owner>__<repo>__local.md`, never into a shared project file, so a later snapshot can't collide with their entry ids. Review and citation lines on shared entries are kept in `memory/overlay/` and re-applied to each new snapshot by entry id.

## Data and privacy

The bundled canon (`canon/`) contains the curated canon files, their sandboxes, Brain's CLI and the memory steward. It excludes Git history, incoming queues, credentials, local `.brain` data, and raw conversations. User data is stored outside the plugin and survives reinstall or upgrade. There is no remote sync.

Run `python scripts/brain.py status` to see the exact local data directory. Override it with `BRAIN_ZANEGPT_DATA`. The directory holds `memory/` (index, projects, sandboxes, overlay, incoming), `ideas/`, `tension/`, and a derived `view/` that can be deleted at any time. A v1 store (`knowledge.json`) is moved into the steward's queue on first run and backed up to `legacy-v1/`.

## CLI

```text
python scripts/brain.py status
python scripts/brain.py query reachability [--verbose]
python scripts/brain.py challenge reachability
python scripts/brain.py mine
python scripts/brain.py sync
python scripts/brain.py train [auto|audit|rebuild|edge|gap|kernel|group|combined|newidea|newdomain]
python scripts/brain.py check <proposal.md> [--answer reply.txt]
python scripts/brain.py paths | analyze | tension | scorecard
python scripts/brain.py export --out brain-local-export.zip
python scripts/brain.py import brain-local-export.zip
```

`import` restores an export exactly into an empty store. Into a store that already has lessons, it re-files each lesson through the steward; review lines then have to be earned again in that store.

## Sources

- <https://github.com/Pappydapimp69/Brain>
- <https://github.com/Pappydapimp69/Zanegpt>
- Brain nodes listed in `canon/MANIFEST.json`

See `THIRD_PARTY_NOTICES.md` before redistribution.
