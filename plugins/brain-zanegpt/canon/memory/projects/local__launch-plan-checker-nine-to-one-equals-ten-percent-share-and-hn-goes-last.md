# local/launch-plan-checker-nine-to-one-equals-ten-percent-share-and-hn-goes-last — lessons

Project: local/launch-plan-checker-nine-to-one-equals-ten-percent-share-and-hn-goes-last. Newest first.

---

## E1 — launch plan checker nine to one equals ten percent share and hn goes last
- Date: 2026-10-18
- Project: local/launch-plan-checker-nine-to-one-equals-ten-percent-share-and-hn-goes-last
- Tags: [distribution][marketing][platform-etiquette][testing][model]
- What: A launch-plan checker built from three distribution kernels treats the 9 to 1 participation rule and the 10 percent self-promo share as the same limit (the same maximum promo posts for every participation count from 0 to 200), flags the misreading of promo as at most 10 percent of participation, which allows one fewer post at 9, 18 and 27 actions, and catches wrong venue order, a Show HN without a playable link and marketing words in its title.
- Why built: Gap pick: three unapplied DISTRIBUTION kernels each state a checkable rule (venue order, 9 to 1, Show HN survival criteria) with no build behind them, and two of them quote the participation limit in different forms.
- Design: A plan is a list of venue posts in the order jam, itch, dedicated subreddit, Show HN; the ratio limit is participation divided by 9 rounded down, compared with a share limit solved by stepping promo posts until promo over promo plus participation exceeds one tenth; promo means dedicated-subreddit and Show HN posts; violations are returned as named problems.
- Got right: Both forms of the limit agreed on all 201 counts, the misreading gave 0, 1 and 2 posts at 9, 18 and 27 actions against the correct 1, 2 and 3, the good plan passed at 27 actions and failed at 26 on the ratio, and each of order, missing playable URL and marketing title was caught.
- Where/why it failed: Nothing in the prediction failed, but the checker only encodes the kernels' stated norms, which the kernel itself rates as medium confidence from marketing-blog sourcing for the Reddit side, and what counts as one participation action or a promo post is my modelling choice, not Reddit's.
- Fix: When planning a launch, count participation actions first and derive the allowed promo posts as participation divided by 9, not 10, and encode venue order and the Show HN criteria as a checklist run before posting.
- Why this fix: A promo share of one tenth is one promo post per nine participation actions, so dividing by 10 silently under-counts the allowance, and the order and the playable-link rule are cheap to check mechanically.
- Rule of thumb: Allowed promo posts are participation divided by 9, equal to a 10 percent promo share, not divided by 10; with 27 actions 3 posts fit, and Show HN goes last with a playable link and no marketing words.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the venue norms themselves come from the kernels and were not checked against Reddit or Hacker News, and no real subreddit was consulted.
- Composed: ideas:DISTRIBUTION/where-to-post-a-free-browser-game, ideas:DISTRIBUTION/reddit-containment-not-prohibition, ideas:DISTRIBUTION/show-hn-survival-criteria
- Picked-by: current-half
- ZaneGPT verdict: weak — the arithmetic equivalence is verified but near-tautological, and the real-world rules, the participation definition and the "playable" test are never checked against any source.
- Hidden assumption: The checker's own definitions (promo = subreddit plus Show HN, participation as a plain action count, "marketing words" as a word list) match what the real communities enforce. The test only proves the code agrees with itself, since the 9:1 and 10 percent limits were built to coincide. Nothing here shows Reddit or HN actually enforces any of it.
- Would prove it wrong: A real subreddit's rules, or a mod removal of a plan that passed (27 actions, 3 promo posts, Show HN last with a playable link), would refute it. So would a title the word list passes that HN flags as marketing, or a 9:1 reading where the promo post itself counts toward the nine.
- Break scenario: Take 28 actions with 3 promo posts. On the "participation" reading, 28 divided by 9 floors to 3, so the plan passes. If the promo posts count as actions, participation is 25, the floor is 2, and the plan fails. The 201-count agreement only covers participation excluding promo, so it says nothing about this case. Add a Show HN titled "Launch: free tool" with an itch link that isn't playable in the browser.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 84a085c10ded
- Sandbox: sandboxes/2026-10-18__launch-plan-checker-nine-to-one-equals-ten-percent-share-and-hn-goes-last.py
- Prediction: Written into the script header before the first run: the 9 to 1 and 10 percent share limits agree on 0 to 200, the divide-by-10 misreading allows one fewer at 9, 18 and 27, and order, URL, marketing voice and ratio violations are each caught while the good plan passes at 27 actions.
- Observed: RESULT: PASS 9:1 equals 10 percent share on 201 counts, misreading allows [(9, 0), (18, 1), (27, 2)], good plan clean at 27 actions, order/url/voice/ratio violations each caught
- Scenarios: 1) ratio against share over 0 to 200; 2) BREAK: promo at most 10 percent of participation at 9, 18 and 27; 3) good plan at 27 and 26 actions; 4) wrong order, no playable URL, marketing title
- Link: scheduled brain train auto loop 2 pass 5; session_01U1GJP4ePDFrmU7psLn9wKR
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E457 · compatible · sandboxes/2026-10-18__reddit-nine-to-one-is-per-subreddit-and-thread-days-set-the-launch-calendar.py · observed RESULT: PASS first promo day 4 (ready day 2, thread day 4); half-split comments 11; two gated subs [4, 11]; show HN day 5 · brain train auto loop 2 pass 1, session_01K8wZ3EDWp7o2YCk1kac5LF
