# local/sandbox-kernel-queueing-theory — lessons

Project: local/sandbox-kernel-queueing-theory. Newest first.

---

## E2 — littles law cap needs headroom for service variability and pooling
- Date: 2026-10-12
- Project: local/sandbox-kernel-queueing-theory
- Tags: [queueing][concurrency][sandbox]
- What: Built a closed-system event simulation of 4 servers to test the Little's-law in-flight cap kernel against the pooling kernel and found the cap equals server count only when all work shares one queue.
- Why built: Both queueing kernels were unapplied by memory; their interaction (a concurrency cap on top of per-server lines) was untested.
- Design: Deterministic event simulation, N jobs circulating through c=4 servers for 4000 time units; fixed service 1.0 versus a repeating mean-1.0 service pattern; one shared FIFO versus round-robin per-server queues; N from 2 to 16.
- Got right: At N=16 throughput was 4.00 per unit and latency 4.0 in every variant, matching L=lambda W (16/4.00); below capacity throughput equalled N (2.00 at N=2).
- Where/why it failed: My prediction was that variable service would leave idle servers at N=c with a shared queue (throughput under 3.9); it stayed 4.00. The real loss was in per-server queues: 3.13 per unit at N=c (22% lost) with latency 1.28 instead of 1.0, recovering to 4.00 by N=6.
- Fix: Set the in-flight cap to server count only behind one shared queue; with per-server lines give headroom (here 1.5x capacity) or pool the lines first.
- Why this fix: A shared queue is work-conserving so any waiting job keeps a free server busy, whereas a per-server line can leave one server idle while another has a backlog, and a cap at c leaves nothing queued to cover that.
- Rule of thumb: A cap of throughput x latency capped at server count is exact only for a shared queue; with separate per-server queues the same cap lost 22% of throughput in this sandbox, so pool the queues or raise the cap.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script in this session; all numbers are from that run.
- Composed: ideas:QUEUEING/concurrency-limits/size-in-flight-work-by-littles-law, ideas:QUEUEING/pooling/one-shared-queue-beats-a-queue-per-server, sandbox-kernel-queueing-theory/E1
- Sandbox: sandboxes/2026-10-12__littles-law-cap-needs-headroom-for-service-variability-and-pooling.py
- Prediction: N=16 gives throughput 4.00 and latency 4.0; variable service at N=c with a shared queue leaves servers idle (below 3.9); separate queues lose throughput at N=c.
- Observed: RESULT: PASS cap N=c holds for a shared queue (4.00/s) but per-server queues drop to 3.13/s at N=c; shared-queue prediction of idle servers was refuted (4.00).
- Scenarios: 1) fixed service shared N=2..16; 2) BREAK: variable service shared at N=c; 3) variable service per-server queues N=2..16; 4) Little check L=lambda W at N=16
- Link: brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh

## E1 — square root staffing matches erlang c within one server
- Date: 2026-10-12
- Project: local/sandbox-kernel-queueing-theory
- Tags: [queueing][staffing][capacity][measurement]
- What: Seed of a new domain, queueing theory: whether the square-root staffing rule (servers = load plus
  beta times the square root of load, beta from the Halfin-Whitt waiting limit) gives the right number of
  servers for a target chance of waiting, checked against the exact Erlang C answer.
- Why built: Brain had no queueing kernels (queries for erlang, staffing and littles returned nothing
  relevant), yet sizing a pool of servers, workers or match slots against random arrivals comes up in
  games, services and tooling alike, and the square-root rule is the usual shortcut.
- Design: Exact and deterministic. Erlang C computed by the Erlang B recursion and cross-checked against
  a directly solved M/M/s birth-death chain. beta solved by bisection from alpha = 1/(1 + beta Phi/phi).
  Loads 0.5 to 500, targets 0.5, 0.2, 0.05, 0.01; rule ceil(R + beta sqrt R) against the smallest exact s;
  pooling two loads of 100 at alpha 0.2. Isolated: no existing Brain entry is exercised.
- Got right: Erlang C matched the chain to 6.7e-16; beta came out 0.51, 1.06, 1.74, 2.37; the rule was
  within one server of exact in all 44 cells, including loads of 0.5 to 3; at R = 10000 the exact wait
  chance at the rule's s was 0.498, 0.202, 0.051, 0.0105, matching the limit; pooling saved 6 servers
  against a predicted 6.2.
- Where/why it failed: The error is one-sided: the bare rule was 1 server SHORT of exact in 25 of 44 cells
  and never over, mostly at strict targets (every cell at alpha 0.01), so used as-is it misses the wait
  target. My prediction expected errors in both directions.
- Fix: Staff ceil(R + beta sqrt R) + 1, or use the rule as the starting point and step up with exact
  Erlang C until the target holds; plan with pooled queues, since spare capacity grows as sqrt R.
- Why this fix: The +1 was never short in any tested cell and costs at most one server, while the exact
  check is a ten-line function; both keep the square-root rule's intuition for pooling.
- Rule of thumb: For a pool of servers facing random arrivals, staff ceil(R + beta sqrt R) + 1 (beta 0.51,
  1.06, 1.74, 2.37 for a 50, 20, 5, 1 percent chance of waiting): the bare rule was 1 short of exact Erlang
  C in 25 of 44 cases and never over; pooling two loads of 100 saved 6 servers.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4;
  numbers copied from the run); the Erlang C formula and the Halfin-Whitt beta = (1 - rho) sqrt(s)
  relation were read on Wikipedia pages citing Halfin and Whitt 1981. The model assumes Poisson arrivals
  and exponential service, which real queues only approximate.
- Composed: N/A
- Sandbox: sandboxes/2026-10-12__square-root-staffing-matches-erlang-c-within-one-server.py
- Prediction: Erlang C equals the chain to 1e-12; beta about 0.50, 1.06, 1.74, 2.38; the rule within one
  server of exact for loads 5 to 500 at all four targets; at loads 1 to 2 and alpha 0.01 still within one;
  pooling two loads of 100 at alpha 0.2 saves about 6, within 2.
- Observed: RESULT: PASS 4/4; rule short 25/44 over 0; worst rule error R>=5 1, R<=3 1; pooling saved 6
  vs 6.2; betas [0.51, 1.06, 1.74, 2.37]
- Scenarios: 1) formula against the birth-death chain; 2) loads 5 to 500 at four targets; 3) built to
  BREAK the claim: loads 0.5 to 3, where the heavy-traffic limit should be weakest; 4) pooling two loads.
- Link: session; brain train newdomain (QUEUEING-THEORY seed); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-queueing-theory.md#E2 · compatible · sandboxes/2026-10-12__littles-law-cap-needs-headroom-for-service-variability-and-pooling.py · observed RESULT: PASS cap N=c holds for a shared queue (4.00/s) but per-server queues drop to 3.13/s at N=c; shared-queue prediction of idle servers was refuted (4.00). · brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E42 · compatible · no sandbox · observed Best net 82 at 6 servers (81 at 5, 76 at 8, 34 at 2); prediction refuted by two servers. · games/lobby/game.js SEASON 2; session_011p52L2CkFXcsYRwjDu6tG9
