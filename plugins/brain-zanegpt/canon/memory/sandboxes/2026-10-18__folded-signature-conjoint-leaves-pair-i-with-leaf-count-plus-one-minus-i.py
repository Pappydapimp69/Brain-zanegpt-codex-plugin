# Bookbinding imposition. A strip of M = 2**k panels is folded in half k times into a signature
# of M leaves (N = 2*M pages). Fold physically (stack of layers, each (panel, face_up)), then read
# the stack top to bottom as a book: leaf i has recto = 2i-1 and verso = 2i.
# PREDICTION (before run): for k = 1..4 the two panels that face each other across a fold
# (0,1), (2,3), ... carry book leaves l and l' with l + l' = M+1 (conjoint leaves), the page
# numbers they show on the same strip face sum to N+1 = 2M+1, and the blank pages needed to reach
# a multiple of 4 pages are (-pages) % 4: 10 pages need 2, 12 need 0, 30 need 2.
def fold_once(stack):
    """stack: list of layers (top first), each layer a list of (panel, up) in order across the width.
    Fold right half over left half; right half flips and reverses."""
    width = len(stack[0])
    half = width // 2
    left = [[c for c in layer[:half]] for layer in stack]
    right = [[(p, not up) for (p, up) in reversed(layer[half:])] for layer in stack]
    # right half lies on top of the left half, reversed layer order (flipped over)
    return list(reversed(right)) + left
def build(k):
    M = 2 ** k
    stack = [[(p, True) for p in range(M)]]
    for _ in range(k): stack = fold_once(stack)
    # now a single column: stack is list of layers of one cell
    layers = [layer[0] for layer in stack]
    return M, layers
ok = True; summary = []
for k in range(1, 5):
    M, layers = build(k)
    N = 2 * M
    leaf_of = {panel: i + 1 for i, (panel, up) in enumerate(layers)}
    face_page = {}                                   # (panel, face) -> page number
    for i, (panel, up) in enumerate(layers):
        recto, verso = 2 * i + 1, 2 * i + 2
        face_page[(panel, "front" if up else "back")] = recto
        face_page[(panel, "back" if up else "front")] = verso
    pair_ok = all(face_page[(j, f)] + face_page[(j + 1, f)] == N + 1 for j in range(0, M - 1, 2) for f in ("front", "back"))
    leaf_ok = all(leaf_of[j] + leaf_of[j + 1] == M + 1 for j in range(0, M - 1, 2))
    summary.append((k, M, N, pair_ok, leaf_ok))
    ok = ok and pair_ok and leaf_ok
    print("k", k, "leaves", M, "pages", N, "front", [face_page[(j, "front")] for j in range(M)], "back", [face_page[(j, "back")] for j in range(M)])
blanks = {10: (-10) % 4, 12: (-12) % 4, 30: (-30) % 4}
print("blanks", blanks)
ok = ok and blanks == {10: 2, 12: 0, 30: 2}
print("RESULT: %s folded strips k=1..4: facing panel pairs (0,1),(2,3).. sum to N+1 pages and conjoint leaves sum to M+1 in %s; blanks 10->2, 12->0, 30->2"
      % ("PASS" if ok else "FAIL", [(k, p and l) for k, M, N, p, l in summary]))
