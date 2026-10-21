# local/codex-visual-snapshots — lessons

Project: local/codex-visual-snapshots. Newest first.

---

## E1 — browser rendered visual snapshots
- Date: 2026-07-13
- Project: local/codex-visual-snapshots
- Tags: [visualization][browser][testing][tooling]
- What: While updating snapshots for generated Brain visualization HTML files, the first attempt targeted `.codex/snapshots`, assuming a Codex-owned folder inside the workspace would be a natural home for generated visual baselines. Both the browser-side write and a direct workspace shell mkdir failed with permission errors. The successful path was to create a normal project-owned `snapshots/` directory, serve the HTML files over localhost, capture PNGs through the browser, and verify console errors plus screenshot output.
- Why built: The user asked to update snapshots after several animated Brain visualization files were generated. Because there was no conventional snapshot test framework in `package.json`, `scripts/check.mjs`, or `scripts/smoke.mjs`, the actionable interpretation was to create visual PNG snapshots for the current HTML artifacts.
- Design: Serve the target HTML files from a local HTTP server, open each in the in-app browser, wait for load and a short render interval, capture a viewport PNG, hash the screenshot, and check browser console errors. Store the PNGs in a plain workspace directory (`snapshots/`) instead of a tool-owned folder.
- Got right: The final snapshot update rendered the real HTML in a browser instead of copying files or trusting static source inspection. Three PNGs were produced for `brain-growth-phyllotaxis-20260713-063304.html`, `brain-animated-map-20260713-062813.html`, and `brain-coverification-forge-20260713-061637.html`; all had zero browser console errors. The project smoke gate also passed via `npm.cmd run check`.
- Where/why it failed: The first snapshot target, `.codex/snapshots`, failed because the `.codex` subtree was read-only under the current sandbox. Browser-side `mkdir` reported `EPERM`, and direct PowerShell `New-Item` also returned access denied. A second unrelated command issue appeared when `npm run check` invoked PowerShell's blocked `npm.ps1`; the Windows shim `npm.cmd run check` was the correct invocation.
- Fix: Create `snapshots/` at the project root, write the PNG baselines there, and use `npm.cmd` for the verification command on Windows when PowerShell blocks `npm.ps1`.
- Why this fix: The project root is explicitly writable, so `snapshots/` is stable under the sandbox. Rendering over localhost exercises browser behavior, animation startup, canvas layout, and console errors. Using `npm.cmd` calls the same npm script without tripping PowerShell's script execution policy.
- Rule of thumb: For generated visual artifacts, update snapshots only after a browser render pass, and write baselines to a project-owned writable directory. Treat tool-owned folders like `.codex` as read-only unless a write succeeds. On Windows, prefer `npm.cmd` when PowerShell refuses `npm.ps1`.
- Provenance (verified/assumed): Verified first-hand in this session. `.codex/snapshots` creation failed with `EPERM`/access denied; `snapshots/` creation succeeded; browser captures wrote three PNGs with hashes and zero console errors; `npm.cmd run check` printed `Smoke checks passed.`
- Composed: N/A
- Link: snapshots/brain-growth-phyllotaxis-20260713-063304.png; snapshots/brain-animated-map-20260713-062813.png; snapshots/brain-coverification-forge-20260713-061637.png
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E45 · compatible · sandboxes/2026-10-11__render-pass-snapshot-of-animated-page-needs-frozen-clock.py · observed RESULT: PASS 4/4; unfrozen flaky@120 0.80 max 7.68px; frozen 0; static 0 · session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
