# local/sandbox-kernel-ml-benchmarks — lessons

Project: local/sandbox-kernel-ml-benchmarks. Newest first.

---

## E1 — gpt3 few shot superglue win is an average over a split task mix
- Date: 2026-10-09
- Project: local/sandbox-kernel-ml-benchmarks
- Tags: [ml][benchmark][stats][evaluation][verification]
- What: Re-checked the kernel "GPT-3 few-shot with 32 examples beat fine-tuned BERT-Large on SuperGLUE" against the per-task test scores of the source table, instead of trusting the headline average. The headline reproduces (71.8 vs 69.0, SOTA 89.0, recomputed 71.79 / 69.03 / 88.97), but it is the mean of a 4-4 split: GPT-3 wins COPA, WSC, MultiRC, ReCoRD and loses BoolQ, CB, RTE, WiC.
- Why built: The kernel was untested by any memory entry. It is quoted as the empirical basis for prompting-instead-of-fine-tuning, so the useful question was where "beat" stops being true, not whether the two averages are as printed.
- Design: Stdlib sandbox with the eight tasks and 11 sub-metrics from Table 3.8 (task score = mean of its sub-metrics, as the benchmark defines it). Scenarios: recompute the three averages; count wins per task and per sub-metric; drop each single task; drop the two biggest contributors (the scenario built to break the claim); sweep all 6435 task weightings on a step-1/8 grid; swap the metric (first sub-metric only, last only); report the worst-task gap and which tasks sit within 3 points of fine-tuned SOTA.
- Got right: The averages match the table to 0.03; the lead of +2.76 survives every single-task drop (smallest +0.09 after dropping COPA) and both single-sub-metric aggregations (+3.79 and +1.72). Wins are 4 of 8 tasks (6 of 11 sub-metrics), and exactly COPA and ReCoRD land within 3 points of fine-tuned SOTA, matching the paper's prose.
- Where/why it failed: The lead is concentrated. Dropping COPA and ReCoRD turns it into -3.06; the biggest per-task loss is WiC at -20.2 (49.4, chance level) and CB is -15.85, so a +2.8 mean hides a tail of large losses. GPT-3 is ahead in 65.9% of the 6435 task weightings, not all of them; my pre-registered bound for that share was 50-65%, so the sandbox's last line is FAIL by 0.9 point (the headline claim itself held, the fragility estimate was slightly off). A paper claim that fewer than eight examples per task already beat BERT-Large comes from a figure on the dev set and was not exercised here.
- Fix: Quote this result as "ahead on the unweighted mean, 4 of 8 tasks, weak on sentence-pair tasks (WiC, CB, RTE)", and report win count and mean together with the worst-task gap. For any benchmark average used to justify swapping fine-tuning for prompting, re-check the per-task rows on the task type you actually need.
- Why this fix: A single mean over heterogeneous tasks is a weighted vote, and the weights are the benchmark's choice, not yours. The per-task split is the cheapest check and the one that predicts whether the headline transfers to your task.
- Rule of thumb: Few-shot GPT-3 beats fine-tuned BERT-Large on SuperGLUE only as a mean over a 4-4 task split: removing COPA and ReCoRD flips it to -3.06 and WiC is -20.2, so read the per-task rows (and the worst task) before generalizing the headline to your own task type.
- Provenance (verified/assumed): Verified first-hand: table values were extracted from the arXiv PDF text with pdftotext (Table 3.8, test set), and every number in this entry comes from the sandbox run on those values (recomputed averages, 4 of 8 wins, 65.9% of 6435 mixes, -3.06 after dropping two tasks). Assumed: the weighting grid is a synthetic construct of mine and describes the grid alone; in-context learning itself is outside the sandbox.
- Composed: ideas:MACHINE-LEARNING/large-language-models/gpt-3/few-shot-with-32-examples-beat-fine-tuned-bert-large-on-superglue, ideas:STATISTICS/paradoxes/simpsons-paradox/berkeley-1973-admissions-reversed-when-broken-down-by-department, local__age-cutoff-roll-up/E1, sandbox-kernel-dsp-realtime/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__gpt3-few-shot-superglue-win-is-an-average-over-a-split-task-mix.py
- Prediction: Averages recompute to the table within 0.05; GPT-3 wins exactly 4 of 8 tasks; no single-task drop flips the lead but dropping COPA plus ReCoRD does; GPT-3 leads in 50-65% of the 6435 task weightings; worst single-task gap is at least 15 points against GPT-3.
- Observed: RESULT: FAIL lead +2.76 on mean (71.8 vs 69.0) but 4/8 task wins, 65.9% of 6435 task mixes, drop COPA+ReCoRD -> -3.06, worst task WiC -20.2. Seven of eight checks held; only the 50-65% share bound missed (65.9%).
- Scenarios: 1) recompute averages from per-task scores; 2) win count by task and by sub-metric; 3) BREAK: drop each single task, then drop COPA and ReCoRD; 4) BREAK: 6435-mix weighting grid; 5) metric swap (first vs last sub-metric); 6) worst-task gap and nearness to SOTA
- Link: brain train auto pass 1 (kernel mode), sandbox under /tmp/claude-0/trainrun/pass1/memory/

