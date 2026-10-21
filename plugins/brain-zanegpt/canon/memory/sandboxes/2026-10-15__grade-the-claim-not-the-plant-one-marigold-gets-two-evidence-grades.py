# Companion-planting claims graded by (plant, target, setting) vs by plant alone. Attributes are transcribed from the kernel's
# own text (trial evidence, mechanism, setting match). Deterministic, no RNG.
# claim: (plant, target, setting, trial_evidence, mechanism_named, setting_matches_trial)
CLAIMS=[("allium","aphids","intercrop",True,"volatile scent",True),
        ("marigold","root-knot nematode","full-season cover crop",True,"alpha-terthienyl toxin",True),
        ("marigold","root-knot nematode","ornamental interplant",True,"alpha-terthienyl toxin",False),
        ("marigold","aphids/whiteflies/mites","any",True,"none shown",True),     # trial found NO significant effect
        ("fennel","tomato/bean/pea germination","within 3-10 ft",True,"anethole/fenchone",True),
        ("basil","tomato hornworm","interplant",False,"asserted only",False)]
def grade_claim(c):
    plant,target,setting,trial,mech,match=c
    if not trial: return "folklore"
    if mech=="none shown": return "refuted-by-trial"
    if not match: return "unsupported-in-this-setting"
    if plant=="fennel": return "allelopathy(negative)"
    return "scent-masking" if "scent" in mech else "targeted-toxicity"
by_claim=[grade_claim(c) for c in CLAIMS]
# plant-level grade: the best grade any claim of the plant earns, applied to every claim of that plant
good={"scent-masking","targeted-toxicity"}
def plant_grade(p): return "supported" if any(grade_claim(c) in good for c in CLAIMS if c[0]==p) else "not-supported"
wrong=0
for c,g in zip(CLAIMS,by_claim):
    claim_ok = g in good
    plant_ok = plant_grade(c[0])=="supported"
    wrong += claim_ok!=plant_ok
    print(f"{c[0]:9s}{c[1]:30s}{c[2]:24s} claim-grade {g:30s} plant-grade {plant_grade(c[0])}")
marigold=[g for c,g in zip(CLAIMS,by_claim) if c[0]=="marigold"]
ok = len(set(marigold))==3 and wrong==2 and by_claim.count("folklore")==1
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"marigold earns {len(set(marigold))} grades over 3 claims; plant-level grading misgrades {wrong} of {len(CLAIMS)} claims")
