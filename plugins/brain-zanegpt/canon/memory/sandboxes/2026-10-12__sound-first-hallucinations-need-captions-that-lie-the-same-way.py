"""Loop 3: a SOUND-FIRST hallucination style (owner's decision) puts the whole
first stage in audio. Players who cannot hear it get nothing unless captions
carry it, and captions can leak which sounds are real.
Exact, no RNG. Shore-stage events: 10 real sounds and 10 hallucinated sounds.
Audience groups (shares ASSUMED, swept below): HEAR (sound, no captions),
BOTH (sound plus captions on), READ (captions only: deaf, muted, weak speakers).
Caption policies:
  NONE        no captions at all
  REAL-ONLY   only real sounds get captions (hallucinated audio bypasses the
              caption system, a common implementation accident)
  TAGGED      both captioned, hallucinations marked (italics, [?])
  SAME        both captioned identically, no speaker name for unseen voices
For each group: RECEIVED = share of hallucinations they get at all; LEAKED =
share they can tell are hallucinated from the presentation alone (a sound with
no caption, or a tag). EFFECTIVE = received and not leaked.
Audience EFFECTIVE = sum over groups of share * effective.
"""


def group_effect(policy, group):
    if group == "hear":
        return 1.0, 0.0
    if group == "both":
        if policy == "none":
            return 1.0, 0.0
        if policy == "real-only":
            return 1.0, 1.0          # heard, and the missing caption gives it away
        if policy == "tagged":
            return 1.0, 1.0
        return 1.0, 0.0
    # read only
    if policy in ("none", "real-only"):
        return 0.0, 0.0
    if policy == "tagged":
        return 1.0, 1.0
    return 1.0, 0.0


def audience(policy, shares):
    tot = 0.0
    for g, s in shares.items():
        rec, leak = group_effect(policy, g)
        tot += s * rec * (1 - leak)
    return tot


def main():
    mixes = {"mostly hearing": {"hear": 0.6, "both": 0.3, "read": 0.1},
             "caption-heavy": {"hear": 0.3, "both": 0.5, "read": 0.2}}
    rows = {}
    for mname, shares in mixes.items():
        rows[mname] = {p: audience(p, shares) for p in ("none", "real-only", "tagged", "same")}
        print(f"{mname:15s}: share of players for whom the shore hallucinations land, unspoiled: " +
              ", ".join(f"{p} {v:.2f}" for p, v in rows[mname].items()))
    checks = [
        ("identical captions are best in both audiences (1.00)", all(abs(r["same"] - 1.0) < 1e-9 and r["same"] >= max(r.values()) - 1e-9 for r in rows.values())),
        ("captioning only real sounds is WORSE than no captions at all", all(r["real-only"] < r["none"] for r in rows.values())),
        ("tagging hallucinations is the worst policy in a caption-heavy audience",
         rows["caption-heavy"]["tagged"] == min(rows["caption-heavy"].values())),
        ("break case: with no captions a caption-heavy audience still loses only the read-only group",
         abs(rows["caption-heavy"]["none"] - 0.8) < 1e-9),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; "
          + "; ".join(f"{m}: " + "/".join(f"{v:.2f}" for v in r.values()) for m, r in rows.items())
          + " (none/real-only/tagged/same)")


if __name__ == "__main__":
    main()
