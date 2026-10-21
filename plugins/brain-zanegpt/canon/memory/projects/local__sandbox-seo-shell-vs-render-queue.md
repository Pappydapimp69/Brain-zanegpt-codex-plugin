# local/sandbox-seo-shell-vs-render-queue — lessons

Project: local/sandbox-seo-shell-vs-render-queue. Newest first.

---

## E1 — seo shell text vs js render queue vs build prerender
- Date: 2026-10-12
- Project: local/sandbox-seo-shell-vs-render-queue
- Tags: [distribution][seo][pipeline][rendering][sandbox]
- What: A day-stepped toy crawler applied to three SEO kernels. A 200-page JS-only site with a 5-pages-per-day render queue reached full text coverage on day 41 (median page day 22) while shell or prerendered text was indexed on day 1; for a single page the JS penalty equals the queue lag (9 days at a 7-day lag, 1 day at zero lag); a build-time prerender on a 7-day build was stale on 86% of days when content changes daily and 10% of days when it changes every 30 days.
- Why built: The kernels say put text in the shell, prerender at build rather than serve bots different HTML, and skip heavy SEO at hobby scale, but nothing in the canon sized how the render queue, the build cadence and the page count interact, or when each fix stops paying.
- Design: Phase 1 indexes raw-HTML text on day 1; phase 2 is a FIFO render queue of R pages per day after a fixed lag L; kinds of page text are shell, build prerender and JS-only; staleness is counted per day as live content changing after the last build; URL variants of one page collapse under a canonical tag. All rates are assumed parameters, not measured Google behaviour.
- Got right: Queue arithmetic matched the prediction apart from one off-by-one in my formula (41 instead of 40); the lag is the entire penalty for one page; staleness fell from 86% to 10% as content change slowed from daily to monthly, and to 0% at a daily build.
- Where/why it failed: Two scenarios are true by construction and prove nothing: a crawler that never runs scripts indexing 0% of JS-only text, and a canonical tag collapsing 4 URL variants to 1. The sandbox cannot show that Google's real render lag is hours or weeks, or that the mentioned bots skip JS; those stay external claims.
- Fix: For a hobby-scale single page, put real text in the static shell first (cost nothing, removes the queue); add a build prerender only when pages are numerous or text is generated at runtime, and match the build cadence to the content change rate or the snapshot goes stale; use a canonical tag when one page has several URLs.
- Why this fix: The shell fix removes the lag term entirely at one page, the queue term grows linearly with page count (200 pages at 5 per day is 41 days), and the staleness term is set by build interval over change interval, so each fix is chosen by whichever term dominates.
- Rule of thumb: In this toy crawler the JS-only penalty was the queue lag at one page but 41 days at 200 pages with 5 renders per day, so shell text first, prerender when the page count or runtime content makes the queue bite, and rebuild at least as often as content changes (a 7-day build left daily content stale 86% of days). Rates here are assumed, not Google's.
- Provenance (verified/assumed): Verified first-hand by running the attached sandbox; queue and staleness numbers are its output. Real crawler behaviour is an assumption taken from the kernels.
- Composed: ideas:DISTRIBUTION/seo/googlebot-two-phase-crawl-put-text-in-the-shell/dont-assume-same-day-indexing, ideas:DISTRIBUTION/seo/prerender-at-build-not-dynamic-render/static-snapshot-is-the-correct-upgrade-path, ideas:DISTRIBUTION/seo/dont-overinvest-at-hobby-scale/schema-sitemap-backlinks-are-marginal-here
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__seo-shell-text-vs-js-render-queue-vs-build-prerender.py
- Prediction: Written before run 1: full coverage on day 40 and median about 20 days for 200 JS pages at 5 per day; single-page penalty equal to the lag, 1 day at zero lag; 86% stale at a 7-day build with daily change and 8 to 16% with monthly change; canonical 4 to 1.
- Observed: RESULT: PASS full coverage day 41, median day 22, single page JS day 9 at lag 7 and day 2 at lag 0, stale share 0.000, 0.857, 0.099 and 0.967 for the four build and change pairs, canonical 4 to 1.
- Scenarios: 1) 200 JS pages queue; 2) single page at lag 7 and lag 0, built to BREAK the claim that JS itself is the cost; 3) crawler without JS; 4) staleness at four build and change rates; 5) four URL variants with and without canonical
- Link: scheduled brain train session, loop 2 pass 5; session_018RFPy3DMrymTRHnMWEoTT9
- Audited: 2026-10-13 · modeled · Read the entry and its stored sandbox (sandboxes/2026-10-12__seo-shell-text-vs-js-render-queue-vs-build-prerender.py). The queue and staleness numbers are computed, not pasted: render_day is a closed form (1 + L + idx//R + 1) giving day 41 and median 22 for 200 pages at 5 per day, and stale_share walks 3600 days and gives 0.857 at a 7-day build with daily change. But the model's rules are hand-written assumptions, and S3 (a no-JS bot indexes 0% of JS text) and S5 (canonical collapses 4 URLs to 1) return values the code builds in by construction, as the entry itself admits. The Rule of thumb is about how real Googlebot's render queue behaves, and the rates are assumed, so the sandbox shows structure only and the real-system part is untested; hence modeled, not pass. · scheduled brain train audit, session_01L8S9oqJa4aBbRJii1PPFmJ
