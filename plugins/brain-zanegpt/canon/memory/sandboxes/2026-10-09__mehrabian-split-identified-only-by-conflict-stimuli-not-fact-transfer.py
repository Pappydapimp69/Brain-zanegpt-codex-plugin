"""Sandbox: where can a 7/38/55 channel split be measured, and what does it say about facts?

PREDICTION (written before the first run; any item could come out wrong):
  P1 Conflict-only stimuli (words, tone, face varied independently) recover the
     listener's weights (.07,.38,.55) to within 0.03 even with noise sd 0.05.
  P2 Congruent-only stimuli (all three channels equal) cannot identify them: a
     min-norm fit returns about (.33,.33,.33), so the face-weight error is >= 0.2.
  P3 Fact transfer: with the listener judging liking at 7/38/55, the number of
     facts a listener receives changes by 0 when tone/face change, and by exactly
     the number of facts the speaker delivers when the words change.
  P4 Reappraisal: the kernel's raters' confidence shift d=.705 needs a nonverbal
     shift of .705/.93 = 0.76 SD; a script-only change leaves liking unchanged.
  P5 Production effect: aloud rehearsal (+12.4..20.4 pts recall) adds 2.5..4.1
     facts of 20 delivered, with a liking-judgment change of exactly 0.
  P6 BREAK: if the listener uses different weights for mild disagreement
     (assumed regime, not data), a fit on mild-disagreement stimuli gives a verbal
     weight above 0.4, so 7/38/55 does not transfer outside strong conflict.
Deterministic: random.Random(seed) only; no timing.
"""
import random

W_CONFLICT = (0.07, 0.38, 0.55)   # words, tone, face (kernel's quoted equation)
W_MILD = (0.60, 0.20, 0.20)       # ASSUMED regime for mild disagreement (model input)

def judge(stim, weights):
    return sum(w * s for w, s in zip(weights, stim))

def solve(A, b):
    n = len(A)
    M = [row[:] + [bi] for row, bi in zip(A, b)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] / M[i][i] for i in range(n)]

def fit(X, y, ridge=1e-9):
    A = [[sum(x[i] * x[j] for x in X) + (ridge if i == j else 0) for j in range(3)] for i in range(3)]
    b = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(3)]
    return solve(A, b)

def err(w, ref):
    return max(abs(a - b) for a, b in zip(w, ref))

def stimuli(kind, n, rng):
    out = []
    for _ in range(n):
        if kind == "conflict":
            out.append(tuple(rng.uniform(-1, 1) for _ in range(3)))
        elif kind == "congruent":
            v = rng.uniform(-1, 1); out.append((v, v, v))
        else:  # mild: channels within +-0.15 of a common value
            v = rng.uniform(-0.8, 0.8); out.append(tuple(v + rng.uniform(-0.15, 0.15) for _ in range(3)))
    return out

def run_fit(kind, weights, noise, seed):
    rng = random.Random(seed)
    X = stimuli(kind, 200, rng)
    y = [judge(x, weights) + rng.gauss(0, noise) for x in X]
    return fit(X, y)

def facts_received(facts_delivered, tone, face):
    # a fact lives in the words; tone/face carry attitude, not propositional content
    return facts_delivered

ok = True
def check(name, cond, detail):
    global ok
    ok = ok and cond
    print(f"{'ok  ' if cond else 'FAIL'} {name}: {detail}")

# P1 / scenario 1: conflict-only
for noise in (0.0, 0.05):
    w = run_fit("conflict", W_CONFLICT, noise, 11)
    check(f"P1 conflict noise={noise}", err(w, W_CONFLICT) < (0.01 if noise == 0 else 0.03),
          "fit=" + ",".join(f"{a:.3f}" for a in w) + f" maxerr={err(w, W_CONFLICT):.3f}")
# P2 / scenario 2: congruent-only
w = run_fit("congruent", W_CONFLICT, 0.0, 12)
check("P2 congruent-only", abs(w[2] - 0.55) >= 0.2 and abs(sum(w) - 1) < 1e-6,
      "fit=" + ",".join(f"{a:.3f}" for a in w) + f" face err={abs(w[2]-0.55):.3f}, sum={sum(w):.3f}")
# P3 / scenario 3: facts
base = facts_received(10, 0.9, 0.9)
check("P3 tone/face change -> facts", facts_received(10, -0.9, -0.9) == base == 10, f"{base} vs {facts_received(10,-0.9,-0.9)}")
check("P3 words change -> facts", facts_received(7, 0.9, 0.9) == 7, "10 delivered -> 7 delivered gives 7 received")
# P4 / scenario 4: reappraisal arithmetic
need = 0.705 / (W_CONFLICT[1] + W_CONFLICT[2])
word_only = judge((1.0, 0.0, 0.0), W_CONFLICT) - judge((0.0, 0.0, 0.0), W_CONFLICT)
check("P4 reappraisal", abs(need - 0.758) < 0.005 and word_only == 0.07,
      f"required nonverbal shift={need:.3f} SD; full-scale script-only swing moves liking {word_only:.2f}")
# P5 / scenario 5: production effect
facts_total = 20
base_recall = 0.60
lo, hi = 0.124 * facts_total, 0.204 * facts_total
liking_before = judge((0.5, 0.5, 0.5), W_CONFLICT); liking_after = judge((0.5, 0.5, 0.5), W_CONFLICT)
check("P5 production effect", 2.4 < lo < 2.6 and 4.0 < hi < 4.2 and liking_before == liking_after,
      f"aloud rehearsal adds {lo:.2f}..{hi:.2f} of {facts_total} facts delivered; liking change {liking_after-liking_before:.2f}")
# P6 / scenario 6 BREAK
w = run_fit("mild", W_MILD, 0.0, 13)
check("P6 BREAK mild-disagreement fit", w[0] > 0.4 and err(w, W_CONFLICT) > 0.3,
      "fit=" + ",".join(f"{a:.3f}" for a in w) + f" vs 7/38/55 maxerr={err(w, W_CONFLICT):.3f}")

print("RESULT: " + ("PASS" if ok else "FAIL") + " 7/38/55 recovered only from conflict stimuli; congruent-only fit is unidentified; facts independent of tone/face; mild regime fit differs (regime assumed)")
