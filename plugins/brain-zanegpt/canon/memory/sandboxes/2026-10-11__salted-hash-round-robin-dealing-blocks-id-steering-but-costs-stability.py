# Hash-sorted round-robin dealing (cast of ids into K buckets) vs an adversary who chooses a new id to steer its bucket.
import hashlib
K = 6
CAST = ["npc%02d" % i for i in range(41)]          # existing ids, 41 + the attacker's new id = 42

def h(s, salt):
    return hashlib.sha256((salt + "|" + s).encode()).hexdigest()

def deal(ids, salt):
    order = sorted(ids, key=lambda s: (h(s, salt), s))      # stable wide hash + id tie-break
    return {s: i % K for i, s in enumerate(order)}

def steer(target, known_salt, tries=400):
    # attacker predicts the bucket of candidate id using ITS belief about the salt, returns first hit
    for n in range(tries):
        cand = "evil%d" % n
        if deal(CAST + [cand], known_salt)[cand] == target:
            return cand
    return None

res, rows = {}, []
# 1) unsalted: attacker knows the scheme -> every bucket reachable
hits_unsalted = {}
for t in range(K):
    c = steer(t, "")
    hits_unsalted[t] = c is not None and deal(CAST + [c], "")[c] == t
res["a1_unsalted_all_6_buckets_steerable"] = all(hits_unsalted.values())
# 2) deployment salt unknown to attacker: attacker assumes empty salt, real salt differs; success should be about 1/K
real = "deploy-secret-A"
ok = 0
for t in range(K):
    c = steer(t, "")
    ok += deal(CAST + [c], real)[c] == t
res["a2_unknown_salt_success_near_chance"] = ok <= 3     # chance is 1 of 6 per target; allow up to 3 of 6
# 3) leaked salt: manipulable again
c = steer(2, real)
res["a3_leaked_salt_steerable_again"] = deal(CAST + [c], real)[c] == 2
# 4) stability: salt per SESSION reassigns most ids, fixed per DEPLOYMENT reassigns none, unsalted none
def moved(a, b): return sum(a[s] != b[s] for s in a) / len(a)
base = deal(CAST, "")
m_session = moved(deal(CAST, "sess1"), deal(CAST, "sess2"))
m_deploy = moved(deal(CAST, real), deal(CAST, real))
m_unsalted = moved(base, deal(CAST, ""))
# 5) BREAK: per-session salt also breaks save-compat: ids added mid-run move ~half under any salt (round-robin cost)
m_add = moved(deal(CAST, real), {s: b for s, b in deal(CAST + ["late"], real).items() if s in CAST})
res["b1_session_salt_moves_most_ids"] = m_session > 0.6
res["b2_deploy_salt_and_unsalted_stable"] = m_deploy == 0 and m_unsalted == 0
res["b3_adding_an_id_still_moves_about_half_under_salt"] = 0.3 < m_add < 0.8
print("unsalted steerable:", hits_unsalted)
print("unknown-salt hits: %d of %d; leaked-salt steer ok: %s" % (ok, K, res['a3_leaked_salt_steerable_again']))
print("moved fraction: session-salt %.2f deploy-salt %.2f unsalted %.2f add-one-id %.2f" % (m_session, m_deploy, m_unsalted, m_add))
for k, v in res.items(): print(k, v)
print("RESULT:", "PASS" if all(res.values()) else "FAIL",
      "unsalted 6/6 steerable; unknown salt %d/6 hits; leaked 1/1; moved session %.2f deploy %.2f add-one %.2f" % (ok, m_session, m_deploy, m_add))
