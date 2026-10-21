# Prediction (before run): the common temperature correction raises a 1.050 reading taken at 100 F by about 0.0058
# (to ~1.0558) and is ~0 at 60 F; an OG read hot (100 F) and an FG read at 60 F makes the simple ABV formula
# (OG-FG)*131.25 read ~0.76 points too low; and the simple formula diverges from the Hall/Daniels-style refined
# formula by under 0.2 ABV at OG 1.050/FG 1.010 but by over 0.5 at OG 1.100/FG 1.020.
def corr(sg, tf):
    return sg * (1.00130346 - 0.000134722 * tf + 0.00000204052 * tf ** 2 - 0.00000000232820 * tf ** 3)
c100 = corr(1.050, 100); c60 = corr(1.050, 60)
print("S1 1.050 at 100F -> %.4f (+%.4f); at 60F -> %.4f" % (c100, c100 - 1.050, c60))
s1 = 0.004 < c100 - 1.050 < 0.007 and abs(c60 - 1.050) < 0.0006
def simple(og, fg): return (og - fg) * 131.25
def refined(og, fg): return (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)
raw_err = simple(1.050, 1.010) - simple(1.050 - 0.0, 1.010)  # zero by construction, for reference
true_abv = simple(1.050, 1.010)
hot_og_read = 1.050 - (c100 - 1.050)  # what a hydrometer at 100F shows when the sugar is truly 1.050 at calibration
print("S2 hot hydrometer shows %.4f for a true 1.050 wort" % hot_og_read)
# Measured-hot OG (reading uncorrected) vs true:
abv_uncorr = simple(hot_og_read, 1.010); print("S2 ABV true %.2f uncorrected-hot-OG %.2f" % (true_abv, abv_uncorr))
s2 = true_abv - abv_uncorr > 0.5
d1 = abs(simple(1.050, 1.010) - refined(1.050, 1.010)); d2 = abs(simple(1.100, 1.020) - refined(1.100, 1.020))
print("S3 formula gap OG1.050/FG1.010 %.2f ABV; OG1.100/FG1.020 %.2f ABV" % (d1, d2))
s3 = d1 < 0.2 and d2 > 0.5
print("RESULT: %s 1.050 at 100F corrects +%.4f, 60F +%.4f; uncorrected hot OG understates ABV by %.2f; simple vs refined gap %.2f at 1.050/1.010 and %.2f at 1.100/1.020"
      % ("PASS" if (s1 and s2 and s3) else "FAIL", c100 - 1.050, c60 - 1.050, true_abv - abv_uncorr, d1, d2))
