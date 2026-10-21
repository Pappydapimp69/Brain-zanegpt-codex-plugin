# local/sandbox-kernel-dsp-realtime — lessons

Project: local/sandbox-kernel-dsp-realtime. Newest first.

---

## E1 — a shared lock glitches audio through the ui threads stalls
- Date: 2026-09-28
- Project: local/sandbox-kernel-dsp-realtime
- Tags: [dsp][audio][realtime][concurrency]
- What: Applied the ideas kernel that one late audio callback is one glitch whatever the average, so the callback must never allocate or block, and cross-thread traffic should go through a lock-free SPSC ring. It reproduced with means far under the deadline, and a mutex glitched most, because the callback inherits every stall of the thread holding the lock.
- Why built: brain train gap listed the kernel as unapplied. sandbox-combined-audio-realtime/E1 bounded a lock-free drain loop; blocking designs had not been compared.
- Design: 10 simulated minutes of 128-sample blocks at 48 kHz (2667 us deadline), 900 us of DSP per block plus or minus 10%. Four designs: allocation in the callback on 30% of blocks with an assumed rare long stall (0.05% chance of up to 6 ms); a mutex shared with a UI thread that takes it on 2% of blocks and is occasionally preempted while holding it (1% chance of up to 8 ms); a try-lock that skips the update when busy; and an SPSC ring with bounded pops.
- Got right: Reporting glitch counts beside mean latency. Every design averaged 900 to 929 us, a third of the deadline.
- Where/why it failed: Allocation in the callback averaged 901.8 us but its worst block took 6716 us and 27 blocks missed the deadline. The mutex averaged 928.8 us, worst 10365 us, and missed 1643 deadlines, because the callback waited out every preemption of the UI thread holding the lock. The try-lock and the SPSC ring both missed 0, worst about 990 us; the try-lock ran 4669 blocks on stale parameters.
- Fix: Never take a lock the UI thread can hold inside the callback; pass parameters through a preallocated SPSC ring (or atomics), and preallocate voices and buffers. If a lock must stay, try-lock and keep the last parameters.
- Why this fix: A lock makes the callback's worst case the other thread's worst case, including time the scheduler takes it away. A ring or try-lock bounds the callback's own work.
- Rule of thumb: Audio glitches come from the tail, not the mean: every design here averaged about 900 us of a 2667 us deadline, yet allocation in the callback missed 27 deadlines in 10 minutes and a mutex shared with the UI thread missed 1643 (worst 10.4 ms, the UI thread's preemption); an SPSC ring or a try-lock missed none, the try-lock at the cost of 4669 blocks on stale parameters.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b10.py loop 46 in Pappydapimp69/Brain, deterministic seeded model. Observed: glitches 27/1643/0/0, worst 6716/10365/990/991 us, 4669 stale blocks. Assumed: the stall distributions for allocation and UI preemption are illustrative, not measured on a real OS.
- Composed: ideas:DSP/real-time-buffer/no-unbounded-work-in-the-callback/preallocate-plus-lockfree-spsc
- Link: session 2026-09-28, brain train gap batch 10 loop 46
- Sandbox: sandboxes/2026-09-28__train-gap-b10.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-ml-benchmarks.md#E1 · compatible · sandboxes/2026-10-09__gpt3-few-shot-superglue-win-is-an-average-over-a-split-task-mix.py · observed RESULT: FAIL lead +2.76 on mean (71.8 vs 69.0) but 4/8 task wins, 65.9% of 6435 task mixes, drop COPA+ReCoRD -> -3.06, worst task WiC -20.2. Seven of eight checks held; only the 50-65% share bound missed (65.9%). · brain train auto pass 1 (kernel mode), sandbox under /tmp/claude-0/trainrun/pass1/memory/
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E39 · compatible · sandboxes/2026-10-15__xrun-counter-hides-overruns-behind-buffer-depth.py · observed RESULT: FAIL mean 900 us of 2667; 26 callbacks over the period; xrun counter S=1 26, S=2 8, S=3 0 (18 overruns hidden at S=2); 1-in-100 sampler max 990 us; rare-bug zero-xrun pass rate 5 min 89.8%, 1 h 23.6%, 10 h 0.0%. The FAIL is only th… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 5
