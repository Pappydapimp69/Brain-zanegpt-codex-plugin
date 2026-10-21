# Pappydapimp69/Dhw26 — lessons

Project: Pappydapimp69/Dhw26. Newest first.

---

## E4 — list view filter is not the data filter
- Date: 2026-10-10
- Project: Pappydapimp69/Dhw26
- Tags: [tooling][scraping][local-events]
- What: The Denton Halloween event app's list page returned 623 records (approved, not yet ended).
  Its detail page reads a different datasource for the same table that has no filter at all: 832
  records including 195 marked Event Over, 13 Pending and 1 Denied.
- Why built: The guide needed early-October events that had already ended; the list feed had
  dropped them and archive.org was unreachable from the environment.
- Design: Paginate the detail page's datasource (POST to its records endpoint without a record id,
  pagingOption offset/count) instead of the list block's; filter approval status ourselves
  (Approved + Event Over shown, Pending/Denied/Cancelled skipped).
- Got right: One request family now returns full fields (address, links, photos) for every record,
  replacing 624 calls (list + one detail call per record) with about 17.
- Where/why it failed: The first pipeline treated the list page's visible set as the dataset, so it
  built an archive to preserve ended events that the source had all along, and early October looked
  empty. The unfiltered source lacks the Tags field, so ended events need inferred tags.
- Fix: tools/fetch_all.js reads the detail datasource; tags come from the list feed when present,
  else from the archive, else keyword inference marked TagsInferred.
- Why this fix: In no-code apps (Softr, Airtable interfaces) filters live on each page block, not on
  the table; a different block on another page can expose the unfiltered table with the same auth.
- Rule of thumb: In a no-code app, a page block's filter is not the data's filter: before archiving around a missing slice, check other pages' blocks (detail pages especially) for an unfiltered datasource on the same table, and apply status filters yourself.
- Provenance (verified/assumed): Verified first-hand: list datasource total 623, detail datasource total 832 on the same day, status counts Approved 623 / Event Over 195 / Pending 13 / Denied 1, both fetched with count == total.
- Composed: pappydapimp69__dhw26/E2, pappydapimp69__dhw26/E3
- Link: https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 4c3e7b5

## E3 — upcoming only feed archive by end date
- Date: 2026-10-09
- Project: Pappydapimp69/Dhw26
- Tags: [data][scraping][local-events]
- What: The Denton Halloween event database only returns events that have not ended yet, so each
  refetch silently loses past events; the guide's October calendar would show early-month days as
  nearly empty after a plain rebuild.
- Why built: A month-long event guide needs past days to stay browsable (the calendar heat map and
  "show ended events" toggle), while the source treats ended events as gone.
- Design: Merge each fetch into a committed archive keyed by record id. A record missing from the
  new fetch is kept only if its end time has passed (it aged out); one that disappears before its
  end time is treated as cancelled or unapproved and dropped.
- Got right: The rule needs no extra API call or status field: the record's own end time explains
  its absence. Photo URLs (which expire) are stripped before archiving.
- Where/why it failed: Two obvious strategies are wrong. Replacing the archive with each fetch
  drops events that ended normally. Keeping everything ever seen resurrects cancelled events, which
  would then show as live in the guide.
- Fix: Keep-if-ended merge in tools/build_db.py merge_archive(); fetch_list.js also refuses to write
  a fetch whose unique count is below the reported total, so a short fetch cannot look like mass
  cancellation.
- Why this fix: Absence is ambiguous in an upcoming-only feed; the end timestamp is the one field
  that disambiguates aging out from removal, and the count guard stops a partial fetch from being
  misread as removals.
- Rule of thumb: When a feed returns only upcoming records, archive across fetches and explain each missing record by its own end time: ended means aged out (keep), not yet ended means removed (drop); never plain-replace or keep-all, and refuse short fetches.
- Provenance (verified/assumed): Verified first-hand: the sandbox reproduced all three strategies, and the real merge on the 623-record fetch kept an artificially ended record and dropped an early-vanished one (622 of 623).
- Composed: pappydapimp69__dhw26/E2
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__upcoming-only-feed-archive-by-end-date.py
- Prediction: replace keeps only late+live (loses aged); keep-all also returns cancelled; end-date rule returns exactly aged, late, live.
- Observed: RESULT: PASS end-date rule ['aged', 'late', 'live']; replace loses aged ['late', 'live']; keep-all resurrects cancelled ['aged', 'cancelled', 'late', 'live']
- Scenarios: 1) record ends between fetches (aged out); 2) record still live; 3) record removed before its end — BUILT TO BREAK keep-all; 4) record added between fetches
- Link: https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 7da6214
- Cited-by: 2026-10-10 · projects/pappydapimp69__dhw26.md#E4 · compatible · no sandbox · https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 4c3e7b5
- Audited: 2026-10-10 · modeled · Read the entry and its stored sandbox (upcoming-only-feed-archive-by-end-date) and reran it logically against its four-record fixture. The strategies are computed over a simulated feed, so the three outcomes are not hard-coded, and the end-date rule does separate aged-out from cancelled there. But the fixture is built to fit the rule: the cancelled record vanishes at hour 15, before its end at 60, and the feed function encodes that disappearance directly, so the rule is only tested on the case it was designed for. Not exercised: a cancellation noticed only after the record's end time (the rule would keep it, as absence then looks like aging out), a fetch gap spanning both the cancellation and the end, a record rescheduled to an earlier end, clock or timezone skew in the end field, and the stated short-fetch refusal guard (the Rule says refuse short fetches, but the sandbox never runs it). The real-data check (622 of 623 on the live fetch) is described in Provenance but is not part of the shipped sandbox, so the claim about the real Denton feed rests on a hand-written model plus an unshipped manual run. Verdict is modeled, not fail: the narrow claim (replace and keep-all are wrong, end-date merge is right on this fixture) holds. · scheduled brain train auto loop 2 pass 3 (audit); session_01PQ4jLSc8kGvXwYbpjoS24m

## E2 — empty events page replay embedded app api
- Date: 2026-10-09
- Project: Pappydapimp69/Dhw26
- Tags: [tooling][scraping][local-events]
- What: dentonhalloween.com/events advertised 300+ events but rendered zero listings to WebFetch and
  to a plain headless render. The real calendar lived in a separate no-code app (Softr backed by
  Airtable) reached only by "learn more" links; its list API returned 623 approved records.
- Why built: Needed the complete official event list for a Halloween guide; news roundups covered
  about 13 events each and most events had no detail page of their own.
- Design: Load the app in headless Chromium, capture the first POST to its /v1/datasource/ list
  endpoint (URL, headers, body), then replay it from inside the page with pagingOption
  {offset, count: 50} until total is reached; then hit the per-record endpoint for every id.
- Got right: Replaying from inside the page context reuses its cookies and headers, so no auth
  reverse-engineering was needed; all 623 list rows and 623 detail records came back, 0 errors.
- Where/why it failed: First replay only patched keys named limit/offset and got 130 of 623; the
  app pages with pagingOption.count, not limit. The list feed also omits address, links and
  ticket URLs, which only the per-record endpoint returns, and recurring events arrive as one
  row per date (404 of 623 rows were repeats). All timestamps are UTC.
- Fix: Set pagingOption explicitly and verify fetched count equals the reported total; fetch
  detail records for the missing fields; collapse rows by normalized title (4+ dates becomes one
  recurring entry with a dates list); convert UTC to America/Chicago before formatting times.
- Why this fix: Checking count against total caught the silent 130-row truncation; the detail
  endpoint was the only place venue and link data existed; collapsing kept daily cocktail menus
  from flooding every day of the list while short series still show on each date.
- Rule of thumb: When an official events page renders empty, look for an embedded no-code app (Softr/Airtable): capture its datasource XHR in a headless browser, replay it in-page with its own paging field, assert fetched == total, and pull per-record details for venue and links.
- Provenance (verified/assumed): Verified first-hand this session: 623/623 list rows and 623 detail records fetched, times cross-checked against independently known events (Blocktober 6-8pm, Nightmare on Brew Street 7pm, Cirque shows), and the 130-row truncation observed before the paging fix.
- Composed: N/A
- Link: https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit c4e8fb2
- Cited-by: 2026-10-09 · projects/pappydapimp69__dhw26.md#E3 · compatible · sandboxes/2026-10-09__upcoming-only-feed-archive-by-end-date.py · observed RESULT: PASS end-date rule ['aged', 'late', 'live']; replace loses aged ['late', 'live']; keep-all resurrects cancelled ['aged', 'cancelled', 'late', 'live'] · https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 7da6214
- Cited-by: 2026-10-10 · projects/pappydapimp69__dhw26.md#E4 · compatible · no sandbox · https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 4c3e7b5

## E1 — event date latest primary beats citation count
- Date: 2026-10-09
- Project: Pappydapimp69/Dhw26
- Tags: [research][local-events][data]
- What: Built a one-page guide to Denton TX's 31 Days of Halloween 2026 by hand-aggregating
  ~46 events from scattered web listings (city calendar, dentonhalloween.com, local news
  roundups, festival site, ticketing pages). Most official pages were JS-rendered/empty or
  linked nowhere, so dates/times had to be reconciled across secondary listings.
- Why built: The official hub lists "300+ events" but its events, haunted-house and tour pages
  rendered no listings to a fetcher, and most events had no detail page, so a single
  trustworthy list did not exist anywhere.
- Design: Each event record stores a link (official page or null) AND a source (where the
  fact was actually found) plus a verified flag. Conflicting dates are resolved by taking the
  most recently published statement from a PRIMARY source (organizer or city), not by how
  many listings repeat a value. Events with no official page show that explicitly.
- Got right: Separating link from source kept dead-link events honest; the page says "no
  official page" instead of linking a 404, and readers can still trace every fact.
- Where/why it failed: Blocktober Pumpkin Drop: a pre-season aggregator (Aug 24) and its
  echoes listed Oct 1, copied from the city's 2025 page; the city's 2026 calendar said Oct 8.
  Majority vote picks Oct 1 (3 vs 2). Distinct-root counting ties 1 vs 1, because the stale
  value ALSO traces back to the authority itself (last year's version of the same page).
- Fix: Resolve by latest-published primary statement; mark verified only when a primary
  source states the value AND at least one other record agrees; otherwise flag unconfirmed.
- Why this fix: Recurring annual events make last year's official page a credible-looking
  root, so root-counting cannot separate them; publish date of the primary statement can.
  Authority-first alone also fails when the city page is stale and the organizer posts a
  newer change, which is why it is latest PRIMARY, not a fixed authority.
- Rule of thumb: For recurring annual events, resolve conflicting dates by the latest-published primary-source statement, not by citation count or distinct roots; stale values usually trace to the authority's own prior-year page.
- Provenance (verified/assumed): Verified first-hand: the Oct 1 vs Oct 8 conflict was observed in fetched sources this session (texashaunts.net Aug 24 post vs City of Denton calendar and dentoncommunityvoice.com), and the sandbox reproduced all three resolver outcomes.
- Composed: local__sandbox-research-methodology/E1, pappydapimp69__brain/E118
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__event-date-latest-primary-beats-citation-count.py
- Prediction: S1 majority picks Oct 1 (wrong), distinct-roots TIE, latest-primary Oct 8; S2 authority-first picks the stale date, latest-primary the organizer's; S3 single-source answers but is not verified.
- Observed: RESULT: PASS latest-primary correct 3/3; majority wrong on S1 (3v2), distinct-roots TIE on S1 (1v1), authority-first wrong on S2, S1 verified, S2+S3 (single agreeing record) flagged unverified
- Scenarios: 1) real Blocktober conflict (stale prior-year root + echoes); 2) stale authority page vs newer organizer post — BUILT TO BREAK authority-first; 3) single-source event (Instagram-only announcement)
- Link: https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 3b74e8b

