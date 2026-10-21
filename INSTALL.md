# Install brain-zanegpt

## Codex CLI

There are two ways to install. Installing from GitHub is the easiest to keep up to date.

### From GitHub

```powershell
codex plugin marketplace add Pappydapimp69/Brain-zanegpt-codex-plugin
codex plugin add brain-zanegpt@brain-zanegpt-repository
```

This needs read access to the repository: it must be public, or your Git credentials must reach it. Add `--ref <branch-or-tag>` to install a specific version instead of `main`.

### From a local folder

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

Installed from GitHub:

```powershell
codex plugin marketplace upgrade brain-zanegpt-repository
codex plugin add brain-zanegpt@brain-zanegpt-repository
```

Installed from a local folder: `marketplace upgrade` only refreshes Git sources, so update the folder itself (`git pull` in a checkout, or extract the new release zip over the old folder), then run:

```powershell
codex plugin add brain-zanegpt@brain-zanegpt-repository
```

To switch a local-folder install to GitHub, remove the marketplace first (Codex refuses the same marketplace name from a second source), then follow **From GitHub**. Your local lessons are not affected:

```powershell
codex plugin marketplace remove brain-zanegpt-repository
```

Either way, restart Codex and check that `brain.py status` reports the new version.

Local lessons remain in the stable user data directory reported by `brain.py status`; they are not stored in or removed with the plugin cache. Upgrading from 1.x moves a `knowledge.json` store into the steward's queue on first run and keeps a backup in `legacy-v1/`.

## Remove

```powershell
codex plugin remove brain-zanegpt@brain-zanegpt-repository
codex plugin marketplace remove brain-zanegpt-repository
```

Removal does not delete the external Brain data directory.
