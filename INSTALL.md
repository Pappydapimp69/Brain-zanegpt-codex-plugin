# Install brain-zanegpt

## Codex CLI

From a checkout or an extracted release of this repository:

```powershell
codex plugin marketplace add "C:\absolute\path\to\brain-zanegpt-repository"
codex plugin add brain-zanegpt@brain-zanegpt-repository
```

Restart Codex or start a new session after installation. Verify the install:

```powershell
codex plugin list --json
python "$env:USERPROFILE\.codex\plugins\cache\brain-zanegpt-repository\brain-zanegpt\2.0.0\scripts\brain.py" status
```

If the cache root differs, use the `installedPath` printed by `codex plugin add` and append `scripts\brain.py`.

## ChatGPT desktop app

Keep the extracted repository in a stable location. Restart the desktop app, open the Plugins Directory, select **Brain ZaneGPT Repository**, and install **Brain ZaneGPT**. The repo-scoped marketplace is `.agents/plugins/marketplace.json`.

## Upgrade

Replace or update the repository, then run:

```powershell
codex plugin marketplace upgrade brain-zanegpt-repository
codex plugin add brain-zanegpt@brain-zanegpt-repository
```

Local lessons remain in the stable user data directory reported by `brain.py status`; they are not stored in or removed with the plugin cache. Upgrading from 1.x moves a `knowledge.json` store into the steward's queue on first run and keeps a backup in `legacy-v1/`.

## Remove

```powershell
codex plugin remove brain-zanegpt@brain-zanegpt-repository
codex plugin marketplace remove brain-zanegpt-repository
```

Removal does not delete the external Brain data directory.
