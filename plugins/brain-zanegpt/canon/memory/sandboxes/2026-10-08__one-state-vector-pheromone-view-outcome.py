"""Gap sandbox: kernel SIMULATION/legibility/one-state-vector-drives-picture-score-and-outcome,
using the pheromone field (SIMULATION/spatial-decay-fields/pheromone-style-per-cell-decay) as the
state vector and a recorded-trace replay (brain-builder/E7). Deterministic, stdlib only."""
RHO = [0.30, 0.30, 0.30, 0.05, 0.05, 0.05, 0.30, 0.30, 0.05, 0.05, 0.30, 0.30]  # exposed vs sheltered
N = len(RHO); TICKS = 40

def step(tau, rho): return [(1 - r) * t for t, r in zip(tau, rho)]
def run(rho, ticks=TICKS):
    tau = [1.0] * N; trace = [tau]
    for _ in range(ticks): tau = step(tau, rho); trace.append(tau)
    return trace
def reach(tau, th):  # tracker follows the trail from cell 0 until strength drops below th
    n = 0
    for t in tau:
        if t < th: break
        n += 1
    return n
def view_extent(tau, th_view): return reach(tau, th_view)   # lit cells shown contiguously from the start
def score(tau): return sum(tau) / len(tau)

TH = 0.2
live = run(RHO)
# S1 single vector: view, outcome from the same tau with the same predicate; replay from stored trace
mis1 = sum(view_extent(t, TH) != reach(t, TH) for t in live)
replay = [list(t) for t in live]                       # view rebuilt from the recorded trace, not re-simulated
mis_replay = sum(view_extent(a, TH) != view_extent(b, TH) for a, b in zip(live, replay))
print(f"S1 one vector: view/outcome mismatches over {len(live)} ticks = {mis1}; trace-replay mismatches = {mis_replay}")

# S2 parallel authored account: view animated with a global mean rho while the model uses per-cell rho
g = sum(RHO) / N
view_only = run([g] * N)
mis2 = sum(view_extent(v, TH) != reach(m, TH) for v, m in zip(view_only, live))
print(f"S2 authored parallel view (global rho={g:.3f}): view != outcome on {mis2}/{len(live)} ticks")

# S3 BREAK: shared vector but different thresholds for picture vs outcome
mis3 = [i for i, t in enumerate(live) if view_extent(t, 0.05) != reach(t, TH)]
print(f"S3 BREAK shared vector, view th=0.05 vs outcome th={TH}: disagree on {len(mis3)} ticks, first at tick {mis3[0] if mis3 else None}")

# S4 sibling kernel: repeated deposit -> steady state d/rho, per cell; outcome from capped tau
d = 0.2; tau = [0.0] * N
for _ in range(400): tau = [(1 - r) * t + d for t, r in zip(tau, RHO)]
err = max(abs(t - d / r) for t, r in zip(tau, RHO))
print(f"S4 steady state max |tau - d/rho| = {err:.2e}; caps exposed {d/0.30:.3f} sheltered {d/0.05:.3f}")

# S5 BREAK: presentation-state sneaks into the vector (view eases toward tau) -> picture lags outcome
eased = [1.0] * N; lag = 0
for t in live:
    eased = [e + 0.5 * (x - e) for e, x in zip(eased, t)]
    lag += view_extent(eased, TH) != reach(t, TH)
print(f"S5 BREAK eased presentation value fed to the picture: disagrees with outcome on {lag}/{len(live)} ticks")

ok = mis1 == 0 and mis_replay == 0 and mis2 > 0 and len(mis3) > 0 and err < 1e-6 and lag > 0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"shared tau agrees ({mis1} mismatches) but only with one shared predicate (S3 {len(mis3)} ticks) and no eased presentation value (S5 {lag}); authored parallel view drifts on {mis2}")
