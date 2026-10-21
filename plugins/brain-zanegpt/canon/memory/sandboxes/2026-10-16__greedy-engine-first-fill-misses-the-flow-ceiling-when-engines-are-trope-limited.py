# 8 engines x 2 skeleton slots, 6 tropes cap R, each engine allowed a window of w consecutive tropes.
# Compare a greedy engine-first fill (engines in order, first allowed trope under cap) with the max-flow optimum.
import itertools
E, T = 8, 6
def allowed(e, w): return [(e + j) % T for j in range(w)]
def greedy(R, w, order):
    cnt = [0]*T; made = 0
    for e in order:
        for t in allowed(e, w):
            if cnt[t] < R: cnt[t] += 1; made += 1; break
    return made
def optimum(R, w):  # slots are 16 (each engine twice); bipartite b-matching by augmenting paths
    slots = [e for e in range(E) for _ in range(2)]
    cap = [R]*T; assign = {t: [] for t in range(T)}
    def try_(s, seen):
        for t in allowed(slots[s], w):
            if t in seen: continue
            seen.add(t)
            if len(assign[t]) < cap[t]: assign[t].append(s); return True
            for s2 in list(assign[t]):
                if try_(s2, seen): assign[t].remove(s2); assign[t].append(s); return True
        return False
    return sum(try_(s, set()) for s in range(len(slots)))
order = [e for e in range(E)]*2
rows = {}
for R in (1, 2, 3):
    for w in (1, 2, 6):
        rows[(R, w)] = (greedy(R, w, order), optimum(R, w))
        print("R=%d w=%d greedy=%d optimum=%d ceiling=%d" % (R, w, *rows[(R, w)], min(16, 6*R)))
gap = max(o - g for g, o in rows.values())
open_ok = all(rows[(R, 6)][0] == rows[(R, 6)][1] == min(16, 6*R) for R in (1, 2, 3))
print("RESULT: %s open engines greedy=optimum=ceiling %s; max greedy shortfall %d at %s; w=1 R=3 greedy %d optimum %d" % (
    "PASS" if open_ok and gap > 0 else "FAIL", open_ok, gap,
    max(rows, key=lambda k: rows[k][1]-rows[k][0]), rows[(3, 1)][0], rows[(3, 1)][1]))
