# local/storyteller-story-quota — lessons

Project: local/storyteller-story-quota. Newest first.

---

## E1 — story a day quota tell the day itself
- Date: 2026-10-17
- Project: local/storyteller-story-quota
- Tags: [narrative][content][cadence][sandbox]
- What: Modelled A Story Short's bargain, one story a day for a year from a stock of 300, under three
  policies: stop when the stock runs out, repeat old stories, or tell the day itself.
- Why built: Brain train on Jim Henson's The StoryTeller; a daily-output cadence with a finite stock is a live
  problem for any regular publishing schedule, and canon had no kernel for its fallback.
- Design: Stdlib loop over 365 days; the stock supplies days 0-299; after that 'stop' ends the run, 'repeat'
  cycles old stories, 'today' tells a new event if the day produced one; exact-duplicate share stands
  in for the AI-video kernel's mass-produced signal; BREAK schedule with one idle day in three.
- Got right: Telling the day covered all 365 days with zero duplicates, against the stock running out on day 300 and
  repeats filling the year at 18 percent duplicates.
- Where/why it failed: The fallback is only as good as the day: with one idle day in three, telling the day failed on day
  300, the first idle day after the stock ran out.
- Fix: Back a daily quota with a renewable source, the day's own events, and protect the days that feed it,
  so the stock is a buffer rather than the plan.
- Why this fix: Repeats keep the count up but read as reruns, while the day's own story is new by construction; the
  only way it fails is a day with nothing in it.
- Rule of thumb: Back a story-a-day quota with the day itself as the fallback, not repeats, and keep the days eventful,
  since an idle day leaves the fallback with nothing to tell.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article and the source-tale pages cited in the kernel. Model parameters are toy values.
- Composed: ideas:AI-VIDEO/monetization-policy/every-video-gets-its-own-joke-and-script
- Sandbox: sandboxes/2026-10-17__story-a-day-quota-tell-the-day-itself.py
- Prediction: Stock alone runs out on day 300; repeats fill the year with some duplicates; telling the day covers
  365 with none; idle days break it.
- Observed: RESULT: PASS stock runs out on day 300; repeats 18 percent duplicates; telling the day 365 with 0
  duplicates; one idle day in three fails on day 300.
- Scenarios: 1) stop when out; 2) repeat old stories; 3) tell the day; 4) BREAK: idle days
- ZaneGPT verdict: weak — the PASS only confirms that code written to cover 365 days covers them when events exist; "tell the day" beating repeats depends on an eventfulness input the rule can't guarantee, and the duplicate metric never tests whether the stories are any good.
- Hidden assumption: Eventfulness is the only gate on "telling the day": that a day producing an event yields a distinct, tellable story at quota quality. The simulation also treats exact-duplicate share as the whole cost of repeats, and nothing else.
- Would prove it wrong: A run where days 300-364 are all eventful, yet telling the day loses to repeats on a quality measure (near-duplicates, thin or low-stakes events, or a shared template). Equally, an idle-day rate where repeats still cover 365 and the fallback's coverage falls below repeats.
- Break scenario: Make events arrive in a correlated streak (a quiet 60-day stretch rather than one idle day in three, same mean rate), and score the stories by distinctness beyond exact match. "Today" then fails in a block, while repeats at 18 percent duplicates still deliver every day. The rule says "keep the days eventful," but you can't control that, and the result says nothing about when repeats are the better fallback.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest eb44de03246a
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

