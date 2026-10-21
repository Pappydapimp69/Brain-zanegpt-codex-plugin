# Sandbox: premise slot machine (6 tropes x 5 study axes = 30 cells) used under the
# anti-template rule (every video its own joke) and the source-check lesson
# (axis labels must be the study's own words). Stdlib, deterministic.
import random, math
TROPES = ["pull_pin","failing_king","number_gates","save_sad_man","merge_bait","stilted_skit"]
AXES_KERNEL = ["gameplay disguise","narrative pretense","borrowed fame","ruleset distortion","incentive illusion"]
AXES_STUDY  = ["gameplay disguise","narrative pretense","popular externalization","ruleset distortion","incentive illusion"]
CELLS = [(t, a) for t in TROPES for a in range(5)]
N = len(CELLS)
def p_cell_collision(k):            # exact birthday over 30 cells
    return 1 - math.prod((N - i) / N for i in range(k))
def p_trope_repeat(k):              # exact birthday over 6 tropes
    return 1 - math.prod((6 - i) / 6 for i in range(k)) if k <= 6 else 1.0
def sim_collision(k, trials=20000, seed=5):
    r = random.Random(seed); hit = 0
    for _ in range(trials):
        d = [r.randrange(N) for _ in range(k)]; hit += len(set(d)) < k
    return hit / trials
# 1) random draw, batch of 10: cell collision probability
p10 = p_cell_collision(10); s10 = sim_collision(10)
print(f"random 10-video batch: P(cell repeats) exact {p10:.3f}, simulated {s10:.3f}")
# 2) rotation without replacement: no cell repeats up to 30 videos
rot = random.Random(1).sample(range(N), N); assert len(set(rot)) == 30
# 3) BREAK: unique cells do not stop trope repetition: first repeated trope at video 7
tropes_seen = set(); first_repeat = None
for i, c in enumerate(rot):
    t = CELLS[c][0]
    if t in tropes_seen and first_repeat is None: first_repeat = i + 1
    tropes_seen.add(t)
print(f"rotating unique cells: first trope repeat at video {first_repeat} (pigeonhole: <= 7); trope-level exact P at 7 videos {p_trope_repeat(7):.1f}")
# best trope-balanced order: round-robin tropes, axes cycling -> trope repeats every 6 videos, unavoidable
# 4) label trace: share of axes findable verbatim in the study's taxonomy
trace_kernel = sum(a in AXES_STUDY for a in AXES_KERNEL) / 5
cells_untraceable = sum(AXES_KERNEL[a] not in AXES_STUDY for _, a in CELLS)
print(f"kernel labels traceable {trace_kernel:.0%}; untraceable cells {cells_untraceable}/30; verbatim labels 5/5 -> 0/30")
ok = (abs(p10 - s10) < 0.02 and 0.6 < p10 < 0.8 and first_repeat is not None and first_repeat <= 7
      and trace_kernel == 0.8 and cells_untraceable == 6)
print(f"RESULT: {'PASS' if ok else 'FAIL'} 10 random videos repeat a cell {p10:.2f} (sim {s10:.2f}); rotation avoids cell repeats to 30 but repeats a trope by video {first_repeat}; kernel labels traceable {trace_kernel:.0%} ({cells_untraceable}/30 cells)")
