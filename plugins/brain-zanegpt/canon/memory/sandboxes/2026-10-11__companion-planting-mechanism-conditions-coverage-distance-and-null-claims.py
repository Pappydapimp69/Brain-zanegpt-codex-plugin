# Four companion-planting mechanism buckets as small deterministic models; each effect depends on its own condition.
import math

def nematode_pop(cover, days=120, r=0.06, kill_max=0.99):
    """root-knot juvenile pool; marigold soil coverage fraction scales the daily kill (alpha-terthienyl reaches only
    the soil it occupies). Returns final pool relative to an unplanted control."""
    def run(c):
        J = 100.0
        for _ in range(days):
            J *= (1 + r)
            J *= (1 - kill_max * c * 0.045)
        return J
    return run(cover) / run(0.0)

def aphid_index(mechanism, share):
    """share = planted fraction. allium volatiles disrupt host finding (effect saturates, narrow);
    marigold has no aphid effect; basil-hornworm is a null claim (no trial effect)."""
    eff = {"allium": 0.45 * (1 - math.exp(-share / 0.08)), "marigold": 0.0, "basil": 0.0}[mechanism]
    return 1.0 - eff

def fennel_germination(distance_ft, radius=6.0):
    return 1.0 if distance_ft >= radius else 0.35 + 0.65 * distance_ft / radius

res = {}
inter, cover = nematode_pop(0.10), nematode_pop(0.95)
res["n1_cover_crop_cuts_nematodes_by_90pct"] = cover < 0.10
res["n2_interplant_does_little"] = inter > 0.55 and cover < inter / 5
res["n3_marigold_no_aphid_effect_while_allium_has_one"] = aphid_index("marigold", 0.2) == 1.0 and aphid_index("allium", 0.2) < 0.7
res["n4_basil_null_claim_flat_at_every_share"] = all(aphid_index("basil", s) == 1.0 for s in (0.05, 0.2, 0.5))
res["n5_allium_effect_saturates_narrowly"] = aphid_index("allium", 0.5) - aphid_index("allium", 0.25) < 0.05
res["f1_fennel_inhibits_inside_radius_only"] = fennel_germination(3.0) < 0.7 and fennel_germination(10.0) == 1.0
# layout: drip zones grouped by water need. Same zone = within 3 ft; separate zones 10 ft apart (drip kernel's zoning rule)
zone_mixed = fennel_germination(3.0)         # fennel and tomato share a zone
zone_split = fennel_germination(10.0)        # separate zones
res["z1_zoning_distance_removes_the_allelopathy_cost"] = zone_mixed < 0.7 and zone_split == 1.0
# BREAK: a long pairing list graded by mechanism - folklore entries add nothing; count entries with a real effect
pairs = [("garlic-aphids", "allium", 0.2), ("marigold-aphids", "marigold", 0.2), ("basil-hornworm", "basil", 0.2),
         ("marigold-nematodes-interplanted", None, None), ("marigold-nematodes-cover", None, None)]
real = [p[0] for p in pairs if (p[1] and aphid_index(p[1], p[2]) < 0.95) or p[0] == "marigold-nematodes-cover"]
res["g1_only_2_of_5_listed_pairings_have_a_real_effect"] = real == ["garlic-aphids", "marigold-nematodes-cover"]
print("nematode pool vs control: interplant 10%% = %.2f, cover crop 95%% = %.3f" % (inter, cover))
print("aphid index allium 20%% = %.2f marigold %.2f basil %.2f" % (aphid_index("allium", .2), aphid_index("marigold", .2), aphid_index("basil", .2)))
print("fennel germination same zone 3ft %.2f separate zone 10ft %.2f; real effects: %s" % (zone_mixed, zone_split, real))
for k, v in res.items(): print(k, v)
print("RESULT:", "PASS" if all(res.values()) else "FAIL",
      "nematodes interplant %.2f vs cover %.3f; aphids allium %.2f marigold %.2f basil %.2f; fennel same-zone %.2f vs split %.2f; 2 of 5 pairings real" %
      (inter, cover, aphid_index("allium", .2), aphid_index("marigold", .2), aphid_index("basil", .2), zone_mixed, zone_split))
