# Deterministic booking checks in integer minutes. Day 09:00-17:00 = 540..1020.
from itertools import combinations
def overlap_closed(a, b): return a[0] <= b[1] and b[0] <= a[1]       # [s,e] inclusive both ends
def overlap_half(a, b): return a[0] < b[1] and b[0] < a[1]           # [s,e)
def conflicts(bk, f): return sum(1 for a, b in combinations(bk, 2) if f(a, b))
def merge(iv, touch):                                                  # touch=True merges adjacent intervals
    out = []
    for s, e in sorted(iv):
        if out and (s <= out[-1][1] if touch else s < out[-1][1]): out[-1] = (out[-1][0], max(out[-1][1], e))
        else: out.append((s, e))
    return out
# 1) back-to-back day: eight one-hour meetings 9..17 with no overlap anywhere
b2b = [(540 + 60 * i, 600 + 60 * i) for i in range(8)]
# 2) true 1-minute overlaps between neighbours
real = [(540 + 59 * i, 600 + 59 * i + 1 * 0 + 0) for i in range(8)]
real = [(540 + 59 * i, 540 + 59 * i + 60) for i in range(8)]
# 3) BREAK: zero-length marker (a 10:00 reminder) among back-to-back meetings
marks = b2b + [(600, 600)]
c = {"b2b": (conflicts(b2b, overlap_closed), conflicts(b2b, overlap_half)),
     "real": (conflicts(real, overlap_closed), conflicts(real, overlap_half)),
     "marker": (conflicts(marks, overlap_closed), conflicts(marks, overlap_half))}
m_touch, m_gap = merge(b2b, True), merge(b2b, False)
free = lambda blocks: (1020 - 540) - sum(e - s for s, e in blocks)
print("conflicts closed vs half-open:", c)
print("blocks after merge: touching-merges", len(m_touch), "| keep-seams", len(m_gap), "| free minutes", free(m_touch), free(m_gap))
ok = (c["b2b"] == (7, 0) and c["real"][0] == c["real"][1] == 7 and c["marker"][0] > c["marker"][1]
      and len(m_touch) == 1 and len(m_gap) == 8 and free(m_touch) == free(m_gap) == 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} back-to-back day: closed ends report {c['b2b'][0]} false conflicts, half-open {c['b2b'][1]}; real 1-minute overlaps caught by both ({c['real'][1]}); zero-length marker conflicts {c['marker'][0]} closed vs {c['marker'][1]} half-open; merge-touching gives {len(m_touch)} block vs {len(m_gap)}, free time identical {free(m_touch)}")
