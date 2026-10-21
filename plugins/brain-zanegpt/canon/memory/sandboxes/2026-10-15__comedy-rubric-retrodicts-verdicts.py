"""Sandbox: do features from the new COMEDY-CRAFT kernels separate the shorts the user liked from the one
they called stupid? Deterministic, stdlib only. Coding is post hoc by the author, who knew the verdicts:
treat this as a consistency check of the rubric, not an independent test.

Features (1 = present), coded per short from its script and render:
  A agency   - a character with a visible want acts on the world (game-of-the-scene lead / Jones' fanatic)
  B physical - the payoff is a visible action or sight gag (Carroll type), not a label or a word
  C fresh    - premise is NOT its stock/hack form (hack-premise check)
  D one_game - every beat heightens or explores the same first unusual thing (no X beats)
  E benign_v - a payoff that is a violation and benign at once (a real success destroyed, cartoon distance)
Verdicts are the user's words in this session: liked / mixed / disliked; None = no verdict given."""

SHORTS = {
    #                    A  B  C  D  E   verdict
    'PLEASE HOLD':      (1, 1, 0, 1, 1, 'liked'),     # "That's funny."
    'SAFE MODE 90':     (1, 1, 0, 1, 1, 'liked'),     # "Now you're getting somewhere with the story"
    'ONLY 1% v1':       (1, 1, 1, 0, 1, 'mixed'),     # liked the knight steering the cursor; "shouldn't reference it's an ad"
    'ONLY 1% v2':       (1, 1, 1, 1, 1, 'liked'),     # the user's own ending: drain, gold, lava ("That's comedy.")
    'STICK SWARM':      (1, 1, 0, 1, 1, None),        # no verdict; user moved on
    'PRIMORDIAL PAIRS': (0, 0, 0, 1, 0, 'disliked'),  # "That was stupid."
}
NAMES = 'ABCDE'
RANK = {'liked': 2, 'mixed': 1, 'disliked': 0}

def separates(idx):
    """True if, using only features idx, every disliked short scores strictly below every liked one."""
    rated = [(sum(v[i] for i in idx), v[5]) for v in SHORTS.values() if v[5]]
    liked = [s for s, verdict in rated if verdict == 'liked']
    disliked = [s for s, verdict in rated if verdict == 'disliked']
    return min(liked) > max(disliked), min(liked), max(disliked)

def concordance(idx):
    """Pairwise rank agreement between feature score and verdict over rated shorts (ties in either count as 0.5)."""
    rated = [(sum(v[i] for i in idx), RANK[v[5]]) for v in SHORTS.values() if v[5]]
    agree = total = 0.0
    for i in range(len(rated)):
        for j in range(i + 1, len(rated)):
            ds, dv = rated[i][0] - rated[j][0], rated[i][1] - rated[j][1]
            if dv == 0: continue
            total += 1
            agree += 1 if ds * dv > 0 else (.5 if ds == 0 else 0)
    return agree / total

results = {}
scenarios = {
    'full rubric A-E': [0, 1, 2, 3, 4],
    'agency only (A)': [0],
    'physical payoff only (B)': [1],
    'hack check only (C)  [built to BREAK the "avoid cliches" claim]': [2],
    'one game only (D)': [3],
    'benign violation only (E)': [4],
}
for name, idx in scenarios.items():
    sep, lo, hi = separates(idx)
    results[name] = (sep, concordance(idx))
    print(f"{name:66s} separates={sep!s:5s} liked_min={lo} disliked_max={hi} concordance={concordance(idx):.2f}")

ok = results['full rubric A-E'][0] and results['agency only (A)'][0] and results['physical payoff only (B)'][0] and not results['hack check only (C)  [built to BREAK the "avoid cliches" claim]'][0]
print(f"RESULT: {'PASS' if ok else 'FAIL'} agency and physical payoff each separate liked from disliked (concordance "
      f"{results['agency only (A)'][1]:.2f}/{results['physical payoff only (B)'][1]:.2f}); hack-premise check alone does not "
      f"(concordance {results['hack check only (C)  [built to BREAK the \"avoid cliches\" claim]'][1]:.2f}); n=5 rated, post hoc coding")
