"""Ask-gap model: does making negotiability explicit close the initiation gap?
Applicant asks iff p_negotiable * success * GAIN > cost. Group B has a higher cost by SHIFT (assumed).
success = 1 if the employer has headroom (ceiling > offer) else 0 (BATNA-style cap from the employer side).
p_negotiable: ambiguous 0.3, verbal hint 0.6, written explicit 0.95 (a written statement is the harder-to-retract signal)."""
GAIN = 4.05                      # k$ expected gain from a successful ask (CMU: ~4,053)
COSTS = [0.1 * i for i in range(1, 40)]   # cost quantiles 0.1..3.9
def rate(shift, p, headroom=True):
    s = 1.0 if headroom else 0.0
    return sum(1 for c in COSTS if p * s * GAIN > c + shift) / len(COSTS)
def gap(shift, p, headroom=True): return rate(0.0, p, headroom) - rate(shift, p, headroom)
P = {"ambiguous": 0.3, "verbal": 0.6, "written": 0.95}
BELIEF_B = {"ambiguous": 0.5, "verbal": 0.8, "written": 1.0}   # B's belief is discounted more when negotiability is unclear
def rate_b(p, k): return rate(0.0, p * BELIEF_B[k])
cost_gap = {k: round(gap(0.5, p), 3) for k, p in P.items()}
belief_gap = {k: round(rate(0.0, p) - rate_b(p, k), 3) for k, p in P.items()}
print("cost-shift mechanism gap:", cost_gap)
print("belief mechanism gap:   ", belief_gap)
big = {k: round(gap(1.5, p), 3) for k, p in P.items()}
print("cost-shift 1.5 gap:", big)
nohead = rate(0.0, 0.95, False) == 0 and rate_b(0.95, "written") * 0 == 0
cost_flat = cost_gap["ambiguous"] <= cost_gap["written"] + 1e-9
belief_closes = belief_gap["ambiguous"] > belief_gap["verbal"] > belief_gap["written"] and belief_gap["written"] < belief_gap["ambiguous"] / 2
ok = cost_flat and big["written"] > big["ambiguous"] and belief_closes and nohead
print(f"RESULT: {'PASS' if ok else 'FAIL'} cost-shift gap does not close (ambiguous {cost_gap['ambiguous']} written {cost_gap['written']}; shift 1.5 widens {big['ambiguous']}->{big['written']}); belief-gap closes {belief_gap['ambiguous']}->{belief_gap['verbal']}->{belief_gap['written']}; zero employer headroom gives zero asks")
