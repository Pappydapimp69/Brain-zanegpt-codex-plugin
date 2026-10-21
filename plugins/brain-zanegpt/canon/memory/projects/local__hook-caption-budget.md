# local/hook-caption-budget — lessons

Project: local/hook-caption-budget. Newest first.

---

## E1 — hook proposition word budget
- Date: 2026-10-15
- Project: local/hook-caption-budget
- Tags: [game-ads][captions][narrative][testing]
- What: A sound-off ad must make its gap-opening proposition readable within 3 s, which caps it at 8
  to 9 words under BBC subtitle rates (160-180 wpm), about 10 under Netflix's 20 characters
  per second, and 5 under this film engine's caption sizing; the hook kernel's '5-10 words per
  second' is 3.3x BBC's fastest rate and was not found in TikTok's guidance.
- Why built: New-half train pick: tension-as-information-gap with the film project and the hook-in-three-
  seconds kernel. TikTok's guidance (introduce the proposition in the first 3 seconds) and
  sound-off viewing make the proposition a caption-reading problem, and the kernel quotes a
  reading rate far above subtitle standards.
- Design: Six fixed fail-ad propositions from 2 to 13 words. Time to read each under BBC 160 and 180
  wpm, Netflix English adult 20 chars/s, the film engine's 1 + words/2.6 s, and the kernel's
  10 words/s; plus the maximum words readable by 3 s under each.
- Got right: Short propositions fit every standard: 'Save him!', 'Can you save the cat?', 'Pull the right
  pin or he drowns' and the 8-word '1%' line are readable by 3 s at BBC's fast rate (4 of 6),
  so the 3-second proposition rule is achievable with tight copy.
- Where/why it failed: I predicted at most half the propositions would fit under BBC; 4 of 6 did. The kernel's 5-10
  words per second does not survive comparison: at 10 words/s a 13-word line would 'read' in
  1.3 s against 4.3 s at BBC's fastest rate, and this film engine's own sizing (1 s plus 2.6
  words/s) allows only 5 words by 3 s, the strictest of all.
- Fix: Write ad propositions to 8 words or fewer (5 if using this film engine's caption timing),
  check them against a subtitle standard rather than the kernel's 5-10 words/s, and treat that
  figure as unverified until a primary TikTok source is found.
- Why this fix: The information gap only opens if the viewer finishes reading the question in time; reading
  rates from subtitle practice are measured and consistent (2.7 to 3.6 words/s), so a rate
  three times higher would let copy run long enough to miss the 3-second window.
- Rule of thumb: A sound-off hook's proposition must read in 3 s: 8-9 words at BBC 160-180 wpm, ~10 at
  Netflix 20 cps; the kernel's 5-10 words/s is 3x too fast and unverified.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; BBC and Netflix rates from secondary summaries of
  their subtitle guides (primary pages not opened); TikTok's 3-second proposition rule
  confirmed via a quote of TikTok for Business, its words-per-second figure not found.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, film/E19, ideas:GAME-ADS/structure/hook-in-three-seconds-sound-off
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__hook-proposition-word-budget.py
- Prediction: Written before running: by 3 s BBC allows 8-9 words, Netflix about 10, the film engine 5;
  the kernel's 10 words/s is >= 3x BBC's top rate; at most 3 of 6 propositions readable by 3 s
  under BBC.
- Observed: RESULT: FAIL (readable count) by 3 s: BBC 8-9 words, Netflix ~10, film engine 5; kernel's 10
  w/s is 3.3x BBC's fastest; propositions readable by 3 s (BBC fast): 4/6.
- Scenarios: 1) six propositions from 2 to 13 words under BBC slow and fast; 2) Netflix characters per
  second; 3) the film engine's sizing; 4) the kernel's 10 words/s, built to test the kernel's
  own figure.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E14 · compatible · sandboxes/2026-10-15__searchable-phrase-card-loses-its-hashtag-to-a-pasted-footer-and-its-overlay-to-the-three-second-hook.py · observed RESULT: FAIL 5/6; footer-first hides the phrase tag, 61 tags hide all (60 keep); overlay fits alone 5/6 at 180 wpm, with phrase 3/6 (160 wpm 1/6); W6 dupes decide: False vs True. The miss is my 160 wpm count (1 not 2); phrase-length sweep… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 5
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E29 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc
- Audited: 2026-10-18 · modeled · Read the entry and re-ran its stored sandbox. The model computes its numbers (words divided by words per second, characters divided by 20, 1 + words/2.6 for the film engine) and does not assume the answer: 9 and 8 words by 3 s under BBC 180 and 160 wpm, 10 under Netflix, 5 for the film engine, and the kernel's 10 words per second is 3.3 times BBC's fastest rate. The scope matches the Rule of thumb. But the claim is about real subtitle standards and viewer reading, and the sandbox only does arithmetic on rates the entry says came from secondary summaries, with no primary page opened and no reading test. The BBC and Netflix runs also ignore caption onset delay, which the film engine formula includes as a full second, so the 8 to 10 word limits are an upper bound. The sandbox's own RESULT is FAIL on a prediction about how many propositions fit (4 of 6 against at most 3), which the entry reports honestly. Modeled, not a pass. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD loop 2 pass 3 audit
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E439 · compatible · sandboxes/2026-10-18__hook-word-count-vs-warp-cap-and-pause.py · observed RESULT: PASS max hook words under the 1.5 cap = 7; fixed 3 s pause misses by >0.5 s for N=[6, 7, 8, 9, 10]; N=5 lag 0 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E449 · compatible · sandboxes/2026-10-18__hook-caption-warp-cap-plus-pause-budget.py · observed RESULT: PASS fit 5/7/8 words; 8 words needs pause 0.3s even with free warp; 10 impossible; 7 words warp-only vs pause-mix. The free-warp part of the prediction was refuted. · scheduled brain train auto pass 2 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
