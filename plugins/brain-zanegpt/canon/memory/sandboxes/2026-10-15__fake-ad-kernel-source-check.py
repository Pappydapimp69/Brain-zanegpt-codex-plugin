"""External-fact check of COMEDY/fake-mobile-ad/premise-slot-machine kernel against its own
cited sources, fetched 2026-10-15 and transcribed below (quotes):
  sherwood.news/business/mobile-game-ads-industry-fake-misleading (6/14/24):
    'Of the 4,000-plus levels on "Homescapes" at the time, just 10 featured the pin-pulling
     mini games'; Royal Match king-killing ads central 'since Dream Games first released the
     app in 2021'; 'surpassed $3 billion in lifetime user spending'.
  psu.edu news 2025-01-13 (Moradzadeh & Kou, Proc. ACM HCI): 15 games flagged via X Community
    Notes, more than 2,500 reviews; five patterns: gameplay disguise, narrative pretense,
    popular externalization, ruleset distortion, incentive illusion.
PREDICTION (written before fetching the Penn State page): every numeric claim and all five
pattern labels in the kernel match the sources."""
KERNEL = {"homescapes_pin_levels": 10, "homescapes_total_levels": 4000, "royal_match_since": 2021,
          "royal_match_spend_bn": 3, "psu_games": 15, "psu_reviews": 2500,
          "patterns": ["gameplay disguise", "narrative pretense", "borrowed fame", "ruleset distortion", "incentive illusion"]}
SOURCE = {"homescapes_pin_levels": 10, "homescapes_total_levels": 4000, "royal_match_since": 2021,
          "royal_match_spend_bn": 3, "psu_games": 15, "psu_reviews": 2500,
          "patterns": ["gameplay disguise", "narrative pretense", "popular externalization", "ruleset distortion", "incentive illusion"]}
num_keys = [k for k in KERNEL if k != "patterns"]
num_ok = [k for k in num_keys if KERNEL[k] == SOURCE[k]]
pat_ok = [p for p in KERNEL["patterns"] if p in SOURCE["patterns"]]
pat_bad = [(p, s) for p, s in zip(KERNEL["patterns"], SOURCE["patterns"]) if p != s]
print(f"numeric claims matching: {len(num_ok)}/{len(num_keys)}; pattern labels matching: {len(pat_ok)}/5; mismatches: {pat_bad}")
ok = len(num_ok) == len(num_keys) and not pat_bad
print(f"RESULT: {'PASS' if ok else 'FAIL'} {len(num_ok)}/{len(num_keys)} numbers match the sources; labels {len(pat_ok)}/5 - kernel says "
      + "; ".join(f"'{p}', source says '{s}'" for p, s in pat_bad))
