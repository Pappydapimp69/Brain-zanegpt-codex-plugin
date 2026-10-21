# local/sandbox-kernel-testing-harness — lessons

Project: local/sandbox-kernel-testing-harness. Newest first.

---

## E2 — a layer counter probe needs a counter after the action
- Date: 2026-09-28
- Project: local/sandbox-kernel-testing-harness
- Tags: [testing][harness][input][debugging]
- What: Applied the ideas kernel that a remote input fault can be localised in one round trip by showing a counter for the same event at each layer it crosses (DOM, framework input, hit decision). The three counters localised faults at those layers, but a fault after the hit decision makes every counter increment, so the probe reports input as working.
- Why built: brain train gap listed the kernel as unapplied, and memory had no entry on per-layer input probes.
- Design: An input pipeline of four layers: DOM delivery, framework input, hit decision, and the action actually completing. Seven faults: an overlay swallowing events, pointer-events none, framework input disabled, hit testing with the wrong camera, a hit area 30% off, a handler that throws after the hit, and an action gated by game state. 20 taps per fault read through probes of 1 counter (hit), the kernel's 3, and 4 (adding action done). A fault counts as localised when the counters narrow it to exactly its layer.
- Got right: Including faults after the hit decision, where the reporter's 'it does nothing' is still true but every probed layer works.
- Where/why it failed: A single hit counter localised 0 of 7 faults. The kernel's three counters localised all 5 faults in their layers and 0 of the 2 after the hit, where all three counters read 20 of 20 and the probe says input is fine. Adding a counter for the action completing localised 7 of 7. For the 30%-off hit area the three counters read 200, 200 and 135 over 200 taps, a 0.68 ratio that points at the hit layer.
- Fix: End the probe with a counter at the effect the user expects (the action completed, the state changed), not at the last input layer.
- Why this fix: 'It does nothing' describes the effect. A probe that stops at the hit decision can only rule out input layers; a fault in the handler or a state gate is invisible to it.
- Rule of thumb: Per-layer event counters localise an input fault in one round trip only if the last counter sits at the effect the user expects: DOM, input and hit counters found 5 of 7 injected faults and read 20/20/20 for a handler that throws after the hit or an action gated by state, while adding an 'action done' counter found 7 of 7.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b10.py loop 47 in Pappydapimp69/Brain, deterministic. Observed: 0/7, 5/7 and 7/7 localised for 1, 3 and 4 counters; partial fault counters 200/200/135. The pipeline is a model of a browser game's input path, not a real one.
- Composed: ideas:testing/harness/count-the-same-event-at-every-depth
- Link: session 2026-09-28, brain train gap batch 10 loop 47
- Sandbox: sandboxes/2026-09-28__train-gap-b10.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E1 — settle on a signal the reveal emits after it finishes
- Date: 2026-09-28
- Project: local/sandbox-kernel-testing-harness
- Tags: [testing][harness][ui][timing]
- What: Applied the ideas kernel that a polling harness catches a progressive reveal mid-flight and must wait for the settled value, defined by ending punctuation, stability across two polls, or a control that appears afterwards. First sighting failed as claimed, and two of the kernel's three settle rules also failed on ordinary text; only the after-control rule held.
- Why built: brain train gap listed the kernel as unapplied, and memory had no harness entry on progressive reveals.
- Design: 1000 seeded typewriter reveals of one to three sentences joined by periods or commas, 30 to 49 ms per character with a 400 ms pause after each comma or period, and a continue control that appears after the last character. Four harness rules at poll intervals of 50, 200 and 500 ms: first non-empty text, text ending in . ! or ?, text unchanged across two polls, and the continue control present. A run fails when the text asserted is not the full text.
- Got right: Using multi-sentence text with punctuation pauses. Single-sentence text with no pauses makes the ending-punctuation and two-poll rules look as good as the control.
- Where/why it failed: First sighting asserted the wrong text in 1000 of 1000 reveals at every poll interval. Ending punctuation failed in 830, 744 and 638 at 50, 200 and 500 ms, settling on the first sentence of multi-sentence text. Stability across two polls failed in 1000 of 1000 at 50 and 200 ms, settling during the 400 ms punctuation pause, and in 0 at 500 ms, where the poll interval exceeded the pause. The after-control rule failed in 0 at every interval.
- Fix: Settle on a signal the system emits only after the reveal ends (a control, an event, a done flag). If only the text is observable, a two-poll stability check needs a poll interval longer than the longest pause the reveal can make.
- Why this fix: Ending punctuation and stability are properties that intermediate states also have; a signal emitted after completion is not.
- Rule of thumb: Wait for a signal the reveal emits after it finishes: ending punctuation settled early on 638-830 of 1000 multi-sentence reveals, and two identical polls settled early on all 1000 whenever the poll interval (50 or 200 ms) was shorter than a 400 ms punctuation pause, while a control that appears afterwards was right in all 1000 at every interval.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b06.py loop 26 in Pappydapimp69/Brain, deterministic seeded reveals. Observed: first sighting 1000/1000 wrong; ending punctuation 830/744/638; two-poll stability 1000/1000/0; after-control 0/0/0 at 50/200/500 ms.
- Composed: ideas:testing/harness/assert-on-settled-not-first-sighting
- Link: session 2026-09-28, brain train gap batch 6 loop 26
- Sandbox: sandboxes/2026-09-28__train-gap-b06.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

- Cited-by: 2026-10-04 · projects/pappydapimp69__brainwork.md#E380 · compatible · sandboxes/2026-10-04__settle-poll-vs-elapsed-check-detects-late-tick-scheduler.py · observed RESULT: PASS poll_only_pass=3/3 budget_ms=10500 exact:ms=10000,within=True slow16.7:ms=11666,within=False slow3:ms=10300,within=True · scheduled brain train pass 4
