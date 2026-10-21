# Rebuild of: with a bridge, an order-k section predictor never predicts the final chorus (k=1..3); without a bridge it
# does at every k; a post-chorus right after the final chorus is predicted again (re-anchoring).
# Own fixture forms (I=intro, V=verse, C=chorus, P=post-chorus, B=bridge, O=outro). Strict order-k: predict the most
# frequent continuation of the last k sections among earlier occurrences in the SAME song; unseen context -> no guess.
# Ties broken by earliest occurrence. BREAK scenario: the same predictor with back-off to shorter contexts.
def predict(hist, k, backoff):
    for kk in (range(k, -1, -1) if backoff else [k]):
        ctx = tuple(hist[-kk:]) if kk else ()
        if len(hist) < kk: continue
        nexts = [hist[i + kk] for i in range(len(hist) - kk) if tuple(hist[i:i + kk]) == ctx]
        if nexts: return max(nexts, key=lambda s: (nexts.count(s), -nexts.index(s)))
    return None
def hit(form, idx, k, backoff=False): return predict(form[:idx], k, backoff) == form[idx]
def final(form, sec): return max(i for i, s in enumerate(form) if s == sec)
FORMS = {"no bridge": list("IVCVCVCO"), "bridge": list("IVCVCBCO"), "bridge2": list("VCVCBCC"),
         "post-chorus": list("IVCPVCPBCPO")}
res = {}
for name, f in FORMS.items():
    fc = final(f, "C")
    row = {k: hit(f, fc, k) for k in (1, 2, 3)}
    extra = {k: hit(f, fc + 1, k) for k in (1, 2, 3)} if name == "post-chorus" else None
    bo = {k: hit(f, fc, k, True) for k in (1, 2, 3)}
    res[name] = (row, extra, bo)
    print(f"{name:12s} {''.join(f)} final chorus idx {fc}: strict {row}  post-chorus-after {extra}  backoff {bo}")
nb, br, pc = res["no bridge"][0], res["bridge"][0], res["post-chorus"]
ok = all(nb.values()) and not any(br.values()) and not any(pc[0].values()) and pc[1][1]
print("RESULT: %s no-bridge final chorus predicted k1-3 %s; bridge never %s; post-chorus final chorus %s, next post-chorus %s; with back-off bridge final chorus %s" % (
    "PASS" if ok else "FAIL", list(nb.values()), list(br.values()), list(pc[0].values()), list(pc[1].values()), list(res["bridge"][2].values())))
