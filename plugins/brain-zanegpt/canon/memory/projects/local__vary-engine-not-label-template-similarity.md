# local/vary-engine-not-label-template-similarity — lessons

Project: local/vary-engine-not-label-template-similarity. Newest first.

---

## E1 — vary engine not label template similarity
- Date: 2026-10-15
- Project: local/vary-engine-not-label-template-similarity
- Tags: [comedy][game-ads][testing][sandbox]
- What: A toy batch checker for six fake game ads that combines the anti-template rule (a swapped game name is mass-produced), the vary-the-comic-engine rule, and the lesson to verify labels rather than numbers. Content similarity (beat bigrams plus voice, layout, endpoint, length, game name excluded) was 1.00 for a name-swap batch and 0.08 for six really different ads, but 1.00 again for six ads with six different engine labels and identical content.
- Why built: The engine rule is usually applied by assigning labels per idea. I wanted to know whether that label step is enough to avoid a templated batch, or whether it can pass a batch that the template rule would still flag.
- Design: Each ad has an engine label, a beat list, voice, layout and endpoint line. Similarity is Jaccard over beat-to-beat bigrams plus the other fields, pairwise, batch score is the max pair, flag at 0.6. Five batches: name-swap only; six distinct engines and content; six labels over identical content (built to BREAK the label check); distinct engines sharing one endpoint line; distinct engines sharing voice and layout. No randomness.
- Got right: Name-swap scored 1.00 and distinct batches 0.08, matching the prediction. A label-only check (6 distinct labels) passed the relabelled-identical batch while the content check scored it 1.00.
- Where/why it failed: Sharing only the endpoint line scored 0.17 and sharing only voice plus layout 0.27, both under the 0.6 flag, although a shared endpoint is exactly what a viewer noticed in the source kernel. A single whole-ad similarity threshold hides partial skin reuse.
- Fix: Check the batch on content, not labels, and add per-field checks (endpoint, voice, layout, beat structure) that each flag on their own when any two ads match, alongside the pairwise score.
- Why this fix: Per-field equality catches the endpoint and skin reuse the aggregate score diluted from 1.00 to 0.17, and content comparison cannot be satisfied by renaming.
- Rule of thumb: Judge ad-batch variety on content fields, not engine labels: labels were distinct 6 of 6 on a batch with similarity 1.00, and a shared endpoint alone only reached 0.17 on the aggregate score, so check each field pair separately (toy model, my own features, no platform data).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the similarity features and 0.6 threshold are my assumed model, not a platform's detector.
- Composed: ideas:AI-VIDEO/monetization-policy/every-video-gets-its-own-joke-and-script, ideas:COMEDY-CRAFT/ideation/vary-the-comic-engine-not-the-topic, fake-ad-kernel-source-check/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__vary-engine-not-label-template-similarity.py
- Prediction: Name-swap max similarity at least 0.9, distinct batch at most 0.4, relabelled identical content at least 0.9 with 6 distinct labels; wrong if the relabelled batch scored under 0.5. Assumption: the engine label reflects the beat structure.
- Observed: RESULT: PASS name-swap 1.00, distinct 0.08, relabelled-same-content 1.00 (labels distinct=True), shared-end 0.17, shared-skin 0.27
- Scenarios: 1) name swap only; 2) distinct engines and content; 3) labels vary, content identical (BREAK); 4) engines vary, shared endpoint; 5) engines vary, shared voice and layout
- Link: session_01A5ZkeepCfk7CHTSxS7qQ4k

