# Tennis tie-break (ITF rules): first server serves point 1, then the opponent serves points 2-3, the first server 4-5,
# and so on in pairs; players change ends after every 6 points; first to 7 points with a 2-point lead wins.
def server_rule(n): return ((n + 1) // 2) % 2          # n = 0-indexed point; 0 = first server
def server_naive_pairs(n): return (n // 2) % 2          # pairs from the start: AABB...
def server_alternate(n): return n % 2                   # every point
def fairness(f, upto):
    a = sum(f(n) == 0 for n in range(upto)); return a, upto - a
def first_two(f): return [f(n) for n in range(6)]
for name, f in (("rule", server_rule), ("pairs-from-start", server_naive_pairs), ("alternate", server_alternate)):
    print("%-17s first six servers %s  split after 12 pts %s  after 13 pts %s" % (name, first_two(f), fairness(f, 12), fairness(f, 13)))
def tiebreak_len_ok(a, b): return (a >= 7 or b >= 7) and abs(a - b) >= 2
def first_end(scores):  # scoring the shortest legal ends: 7-0 .. 7-5, 8-6, 9-7
    return [s for s in scores if tiebreak_len_ok(*s)]
ends = [(7, k) for k in range(0, 7)] + [(8, 6), (9, 7), (7, 6)]
legal = first_end(ends)
rule_ok = first_two(server_rule) == [0, 1, 1, 0, 0, 1] and fairness(server_rule, 12) == (6, 6)
same_counts = all(fairness(f, u) == fairness(server_rule, u) for f in (server_naive_pairs, server_alternate) for u in (12, 13))
naive_bad = first_two(server_naive_pairs)[:2] == [0, 0] and first_two(server_alternate) != first_two(server_rule) and same_counts
print("legal ends among %d candidate scores: %d (7-6 is not legal: %s)" % (len(ends), len(legal), (7, 6) not in legal))
print("RESULT: %s rule serves 0,1,1,0,0,1 and splits 6-6 after 12 points; the pairs-from-start and one-by-one rotations give the same 12- and 13-point serve counts but the wrong order; 7-6 is illegal" % (
    "PASS" if rule_ok and naive_bad and (7, 6) not in legal else "FAIL"))
