# Sandbox: a shot-list linter that applies three AI-VIDEO kernels at once.
#  K1 (compliance): every product shot must be real footage; an AI shot of the product, even with a reference image, fails.
#  K2 (disclosure): label if the video has realistic AI content (YouTube: realistic only; TikTok: label on by default for any AI).
#  K3 (character bible): the descriptor block must be pasted verbatim in every shot that shows the character.
BIBLE = "Mo, 30s, short black hair, green parka, round glasses"
def lint(shots, platform, labelled):
    v = []
    for s in shots:
        if s["product"] and s["src"] != "real": v.append("K1:" + s["id"])
        if s["char"] and BIBLE not in s["prompt"] and s["src"] == "ai": v.append("K3:" + s["id"])
    realistic_ai = any(s["src"] == "ai" and s["realistic"] for s in shots)
    any_ai = any(s["src"] == "ai" for s in shots)
    need = (realistic_ai if platform == "youtube" else any_ai)
    if need and not labelled: v.append("K2")
    if not need and labelled and platform == "youtube": v.append("K2-over")   # harmless but flagged as unneeded
    return v
def S(i, src, product=False, char=False, realistic=True, prompt=""):
    return dict(id=i, src=src, product=product, char=char, realistic=realistic, prompt=prompt)
good = [S("s1", "real", product=True), S("s2", "ai", char=True, prompt=BIBLE + ", walking"),
        S("s3", "ai", realistic=False, prompt="cartoon sky"), S("s4", "real", product=True)]
ref_only = [S("s1", "ai", product=True, prompt="product from reference image"), good[1]]   # BREAK K1 assumption
drift = [S("s1", "real", product=True), S("s2", "ai", char=True, prompt="Mo in a green coat")]
cartoon = [S("s1", "real", product=True), S("s2", "ai", realistic=False, prompt="cartoon sky")]
r = {
 "good_yt_labelled": lint(good, "youtube", True),
 "good_tt_unlabelled": lint(good, "tiktok", False),
 "ref_only": lint(ref_only, "tiktok", True),
 "drift": lint(drift, "tiktok", True),
 "cartoon_yt_unlabelled": lint(cartoon, "youtube", False),
 "cartoon_tt_unlabelled": lint(cartoon, "tiktok", False),
}
for k, v in r.items(): print(k, v)
ok = (r["good_yt_labelled"] == [] and r["good_tt_unlabelled"] == ["K2"] and r["ref_only"] == ["K1:s1"]
      and r["drift"] == ["K3:s2"] and r["cartoon_yt_unlabelled"] == [] and r["cartoon_tt_unlabelled"] == ["K2"])
print("RESULT: %s 6 shot-list cases: compliant list clean; unlabelled realistic AI trips K2; reference-image-only product shot trips K1; paraphrased character block trips K3; unlabelled cartoon passes on YouTube but not TikTok" % ("PASS" if ok else "FAIL"))
