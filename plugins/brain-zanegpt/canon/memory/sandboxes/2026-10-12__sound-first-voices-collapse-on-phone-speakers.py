"""Loop 4: the sound-first style meets the playback device. seven E55/E61: voices
spread around the head stay intelligible (budget 5 with headphones, all outer);
voices in one place collapse to 2. A phone speaker is effectively one place
(mono, or stereo a few cm apart); laptop/TV stereo gives partial separation.
Exact, no RNG. Each voice talks 0.4 of the time. Device = effective masking
width: headphones 60 degrees (as E55), stereo speakers 150 degrees (only a rough
left/right split survives), phone 360 degrees (everything masks). Inner voices
(share 0.34 inside the head, McCarthy-Jones 2014) mask everyone on any device.
Budget = most voices with at least half the words landing. Then the audience
budget for device mixes (shares ASSUMED).
"""


def outer_mask(n_out, width):
    if n_out <= 1:
        return 0
    gap = 360.0 / n_out
    return sum(1 for k in range(1, n_out) if min(k * gap, 360 - k * gap) <= width + 1e-9)


def landing(n, width, inner_share=0.34, d=0.4):
    k_in = round(inner_share * n)
    n_out = n - k_in
    vals = [(1 - d) ** (n - 1)] * k_in
    vals += [(1 - d) ** (outer_mask(n_out, width) + k_in)] * n_out
    return sum(vals) / n


def budget(width, inner_share=0.34):
    return max(n for n in range(1, 13) if landing(n, width, inner_share) >= 0.5)


def main():
    devices = {"headphones": 60.0, "stereo speakers": 150.0, "phone speaker": 360.0}
    rows = {}
    for dev, w in devices.items():
        rows[dev] = (budget(w, 0.0), budget(w, 0.34))
        print(f"{dev:16s}: budget all-outer {rows[dev][0]}, with 34% inner voices {rows[dev][1]}")
    mixes = {"desktop/headphones": {"headphones": 0.6, "stereo speakers": 0.3, "phone speaker": 0.1},
             "mobile-first": {"headphones": 0.3, "stereo speakers": 0.1, "phone speaker": 0.6}}
    for m, sh in mixes.items():
        worst = min(rows[d][1] for d in sh if sh[d] > 0)
        print(f"{m:19s}: a scene must fit the worst common device -> budget {worst}; "
              f"share on phone speakers {sh['phone speaker']:.0%}")
    checks = [
        ("a phone speaker collapses the all-outer budget to the one-place 2", rows["phone speaker"][0] == 2),
        ("headphones keep a bigger budget than a phone speaker even with 34% inner voices",
         rows["headphones"][1] > rows["phone speaker"][1]),
        ("break case: stereo speakers land between phone and headphones (all-outer)",
         rows["phone speaker"][0] <= rows["stereo speakers"][0] <= rows["headphones"][0]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; budgets all-outer/34%-inner "
          + "; ".join(f"{d} {a}/{b}" for d, (a, b) in rows.items()))


if __name__ == "__main__":
    main()
