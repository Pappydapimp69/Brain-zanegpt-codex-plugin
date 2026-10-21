# Deterministic sandbox: does retrofitting a tier devalue owned items, and where?
# Perception model: a player's belief about an item = its value / the learned ceiling.
# value(tier i) = K**i (crafting-depth kernel: cost grows k^depth); rank(i)=i.
K = 3
def tiers(n): return list(range(1, n + 1))
def rank_perceived(i, n): return i / n                      # rank over learned ceiling
def cost_perceived(i, n): return (K ** i) / (K ** n)        # cost-weighted over ceiling
def loss(f, i_old, n_old, i_new, n_new): return 1 - f(i_new, n_new) / f(i_old, n_old)

# S1 lock: 5 tiers stay 5. top item owned.
s1 = loss(rank_perceived, 5, 5, 5, 5)
# S2 retrofit above top: tier 6 added, owned top item stays tier 5.
s2r = loss(rank_perceived, 5, 5, 5, 6); s2c = loss(cost_perceived, 5, 5, 5, 6)
# mean loss across all owned tiers when a tier is added above
s2all = sum(loss(rank_perceived, i, 5, i, 6) for i in tiers(5)) / 5
# S3 insert at bottom: old tier i becomes i+1 of 6; top item keeps full rank.
s3 = loss(rank_perceived, 5, 5, 6, 6)
# S4 BREAK: insert in the middle (between old 3 and 4); old 4,5 shift to 5,6.
s4_top = loss(rank_perceived, 5, 5, 6, 6)
s4_t3 = loss(rank_perceived, 3, 5, 3, 6)   # tiers below the insertion lose
# S5 repeated retrofits: add 3 tiers above one by one.
s5 = loss(rank_perceived, 5, 5, 5, 8)
print(f"S1 lock          top loss {s1:.3f}")
print(f"S2 above rank    top loss {s2r:.3f} cost-weighted {s2c:.3f} all-tier mean {s2all:.3f}")
print(f"S3 below         top loss {s3:.3f}")
print(f"S4 middle        top loss {s4_top:.3f} tier3 loss {s4_t3:.3f}")
print(f"S5 three above   top loss {s5:.3f}")
ok = abs(s2r-1/6)<1e-9 and s1==0 and s3==0 and s4_top==0 and s2c>s2r and s4_t3>0
print("RESULT: " + ("PASS" if ok else "FAIL") + f" above-insert devalues top by {s2r:.3f} (cost-weighted {s2c:.3f}); below/middle insert leaves top at {s3:.3f} but middle devalues lower tiers {s4_t3:.3f}")
