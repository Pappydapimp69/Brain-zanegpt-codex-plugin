# Sandbox: spoof-ad joke types as two dials (ad LIE axis x game ANSWER type).
# Data = the 14 shipped Demo Disc ad/game pairs, tagged first-hand from README.
# Checks: (1) which cells the disc already uses, (2) a rotation planner fills new
# cells with no adjacent repeat on either dial, (3) where the planner stops working.
AXES = ['disguise', 'narrative', 'crowd', 'rules', 'prize']          # study's 5 lie axes ('crowd' = popular externalization)
ANSWERS = ['genre_swap', 'same_word', 'real_skill', 'backstage', 'role_swap', 'tone_flip', 'payoff_twist']
DISC = [  # name, ad lie axis, how the game answers it
 ('only1','narrative','payoff_twist'), ('stickswarm','disguise','same_word'), ('parkingjam','narrative','genre_swap'),
 ('salon','disguise','tone_flip'), ('blocking','disguise','real_skill'), ('boss','disguise','role_swap'),
 ('lastnote','disguise','tone_flip'), ('thirsty','narrative','payoff_twist'), ('soap','narrative','same_word'),
 ('intern','crowd','payoff_twist'), ('veer','disguise','real_skill'), ('embers','disguise','real_skill'),
 ('goingup','disguise','backstage'), ('faro','prize','real_skill')]
# recipe per answer: what the game is, given the ad's fantasy
RECIPE = {'genre_swap':'an unrelated genre wearing the ad\'s name', 'same_word':'the same noun doing a different verb',
 'real_skill':'the real-world science the ad fakes', 'backstage':'the boring job that makes the ad\'s fantasy run',
 'role_swap':'the other side of the ad\'s fight', 'tone_flip':'the ad\'s mechanic at the opposite volume',
 'payoff_twist':'the ad\'s game, but the promised payoff goes sideways'}
HOOK = {'disguise':'fake gameplay clip', 'narrative':'save-him melodrama', 'crowd':'streamer/leaderboard hype',
 'rules':'a mechanic that breaks its own rules', 'prize':'cash/jackpot promise'}

def usage(pairs):
    a = {x: 0 for x in AXES}; r = {x: 0 for x in ANSWERS}; cells = set()
    for _, ax, an in pairs: a[ax] += 1; r[an] += 1; cells.add((ax, an))
    return a, r, cells

def plan(pairs, n, axes=AXES, answers=ANSWERS):
    """least-used-first, skip used cells, never repeat either dial of the previous ad"""
    a, r, used = usage(pairs); a = dict(a); r = dict(r); used = set(used)
    last = pairs[-1][1:]; out = []
    for _ in range(n):
        best = None
        for ax in axes:
            for an in answers:
                if (ax, an) in used or ax == last[0] or an == last[1]: continue
                key = (a.get(ax, 0) + r.get(an, 0), axes.index(ax), answers.index(an))  # deterministic tie-break
                if best is None or key < best[0]: best = (key, ax, an)
        if best is None: out.append(None); break
        _, ax, an = best; out.append((ax, an)); used.add((ax, an)); a[ax] = a.get(ax, 0) + 1; r[an] = r.get(an, 0) + 1; last = (ax, an)
    return out

def naive(pairs, n):
    """baseline: copy the most-used cell (what 'do what worked' does)"""
    a, r, _ = usage(pairs); ax = max(AXES, key=lambda k: (a[k], -AXES.index(k))); an = max(ANSWERS, key=lambda k: (r[k], -ANSWERS.index(k)))
    return [(ax, an)] * n

def adj_repeats(seq, start):
    prev = start; k = 0
    for c in seq:
        if c[0] == prev[0] or c[1] == prev[1]: k += 1
        prev = c
    return k

def premise(ax, an):
    p = {'ad': HOOK[ax], 'game': RECIPE[an], 'ad_verb': ax, 'game_verb': an}
    return p

a, r, cells = usage(DISC)
print('S1 disc usage  axes:', a); print('              answers:', r)
print('   cells used: %d of %d; axes never used: %s' % (len(cells), len(AXES) * len(ANSWERS), [x for x in AXES if a[x] == 0]))
P = plan(DISC, 8); start = DISC[-1][1:]
print('S2 rotation plan (8 next ads):'); [print('   ', c, '->', premise(*c)['ad'], '| game =', premise(*c)['game']) for c in P]
rot = adj_repeats(P, start); nv = adj_repeats(naive(DISC, 8), start)
new_cells = sum(1 for c in P if c not in cells)
ok_premise = all(premise(*c)['ad_verb'] != premise(*c)['game_verb'] and 'disclaimer' not in str(premise(*c)).lower() for c in P)
print('   adjacent repeats: rotation %d, naive copy-the-hit %d; new cells %d/8; premises disclaimer-free & ad!=game: %s' % (rot, nv, new_cells, ok_premise))
# S3 (built to BREAK it): only one answer type allowed -> no legal next ad exists
B = plan(DISC, 3, answers=['real_skill'])
print('S3 one answer type only (break):', B)
# S4: two answer types, one axis -> alternation forced, cells run out fast
C = plan(DISC, 6, axes=['narrative', 'crowd'], answers=['backstage', 'role_swap'])
print('S4 2 axes x 2 answers:', C)
s3_break = B[0] is None
s4_len = sum(1 for c in C if c)
passed = a['rules'] == 0 and rot == 0 and nv >= 7 and new_cells == 8 and ok_premise and s3_break and s4_len < 6
print('RESULT: %s disc uses %d/35 cells, rules axis 0/14; rotation 0 adjacent repeats vs naive %d, 8/8 new cells; planner fails with 1 answer type and runs dry at %d with 2x2'
      % ('PASS' if passed else 'FAIL', len(cells), nv, s4_len))
