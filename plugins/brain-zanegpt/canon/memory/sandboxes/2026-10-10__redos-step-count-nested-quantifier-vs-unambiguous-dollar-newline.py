"""Prediction (before run): a step-counting backtracking matcher (no timing) shows, on a^n + '!' (non-match),
^(a+)+$ steps roughly doubling per extra 'a' (ratio 1.9-2.1 between n=14 and n=15, >20000 steps at n=16), ^(a|aa)+$ also
exponential (ratio >1.4), while the unambiguous ^a+$ and ^(ab+)+$ stay linear (steps(2n)/steps(n) < 2.5).
The matcher's match/no-match verdict equals Python re on every probe. '$' also accepts one trailing newline: ^(a+)+$ on
'a'*n+'\\n' MATCHES in few steps, but 'a'*n+'\\n!' explodes again. Built to break: a MATCHING input for the nested pattern
(a^n with no suffix) must stay cheap (<= 3n steps), proving cost needs a non-match, not just the pattern.
Deterministic, stdlib only."""
import re
class M:
    def __init__(s, text): s.t = text; s.steps = 0
    def run(s, node, i, k):
        s.steps += 1
        kind = node[0]
        if kind == 'ch':
            return i < len(s.t) and s.t[i] == node[1] and k(i + 1)
        if kind == 'seq':
            def go(j, pos):
                if j == len(node) - 1: return k(pos)
                return s.run(node[j + 1], pos, lambda p: go(j + 1, p))
            return go(0, i)
        if kind == 'alt':
            return any(s.run(n, i, k) for n in node[1:])
        if kind == 'plus':   # greedy one-or-more
            def loop(pos):
                return s.run(node[1], pos, lambda p: (p != pos and loop(p)) or k(p))
            return loop(i)
        if kind == 'end':    # python '$': end, or before a final newline
            return (i == len(s.t) or (i == len(s.t) - 1 and s.t[i] == '\n')) and k(i)
        raise ValueError(kind)
def a(c): return ('ch', c)
PAT = {
 'nested ^(a+)+$': (('seq', ('plus', ('seq', ('plus', a('a')))), ('end',)), r'^(a+)+$'),
 'overlap ^(a|aa)+$': (('seq', ('plus', ('alt', a('a'), ('seq', a('a'), a('a')))), ('end',)), r'^(a|aa)+$'),
 'flat ^a+$': (('seq', ('plus', a('a')), ('end',)), r'^a+$'),
 'unambig ^(ab+)+$': (('seq', ('plus', ('seq', a('a'), ('plus', a('b')))), ('end',)), r'^(ab+)+$'),
}
def steps(name, text):
    node, rx = PAT[name]; m = M(text)
    ok = bool(m.run(node, 0, lambda p: True))
    assert ok == bool(re.match(rx, text)), (name, text)
    return m.steps, ok
res = {}
for name in ('nested ^(a+)+$', 'overlap ^(a|aa)+$', 'flat ^a+$'):
    res[name] = {n: steps(name, 'a' * n + '!')[0] for n in (8, 10, 12, 14, 15, 16)}
res['unambig ^(ab+)+$'] = {n: steps('unambig ^(ab+)+$', 'ab' * n + '!')[0] for n in (8, 16, 32)}
for k, v in res.items(): print(k, v)
nest = res['nested ^(a+)+$']; ov = res['overlap ^(a|aa)+$']; fl = res['flat ^a+$']; ua = res['unambig ^(ab+)+$']
r_nest = nest[15] / nest[14]; r_ov = ov[15] / ov[14]
lin_flat = fl[16] / fl[8]; lin_ua = ua[32] / ua[16]
match_cost = steps('nested ^(a+)+$', 'a' * 16)
nl_match = steps('nested ^(a+)+$', 'a' * 16 + '\n')
nl_boom = steps('nested ^(a+)+$', 'a' * 16 + '\n!')
# oracle cross-check: alternation pattern via re.fullmatch (no $ quirk) agrees with the hand matcher except on the trailing newline
alt_inner = r'(?:a|aa)+'
fm_nl = re.fullmatch(alt_inner, 'aaa\n') is None and bool(re.match(r'^(a|aa)+$', 'aaa\n'))
fm_agree = all(bool(re.fullmatch(alt_inner, t)) == steps('overlap ^(a|aa)+$', t)[1] for t in ['a'*n for n in range(1, 12)] + ['a'*n + '!' for n in range(1, 12)])
print("fullmatch rejects trailing newline that $ accepts:", fm_nl, "| fullmatch agrees with hand matcher on plain probes:", fm_agree)
print("ratios nested %.2f overlap %.2f | flat x2 %.2f unambig x2 %.2f" % (r_nest, r_ov, lin_flat, lin_ua))
print("match a*16:", match_cost, "| a*16+newline:", nl_match, "| a*16+newline+bang:", nl_boom)
ok = 1.9 <= r_nest <= 2.1 and nest[16] > 20000 and r_ov > 1.4 and lin_flat < 2.5 and lin_ua < 2.5 \
     and match_cost[1] and match_cost[0] <= 3 * 16 + 10 and nl_match[1] and nl_match[0] <= 100 and nl_boom[0] > 20000 and fm_nl and fm_agree
print("RESULT:", "PASS" if ok else "FAIL", "nested ratio %.2f (n=16 %d steps) overlap %.2f flat/unambig linear (%.2f,%.2f); matching input %d steps, trailing-newline match %d steps vs newline+bang %d" %
      (r_nest, nest[16], r_ov, lin_flat, lin_ua, match_cost[0], nl_match[0], nl_boom[0]))
