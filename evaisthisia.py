"""Έλεγχος ευαισθησίας και σύγκριση με το 2022.
Καλάθια Eurostat ανά εισοδηματικό πεμπτημόριο (ΕΟΠ 2015, 2020· hbs_str_t223, χωρίς τεκμαρτό ενοίκιο)
και καλάθι ΕΟΠ 2025 (ΕΛΣΤΑΤ, Πίνακας 15) × Εναρμονισμένος ΔΤΚ (prc_hicp_minr, ECOICOP 2).
Τρέξιμο: python3 evaisthisia.py  (χρειάζεται μόνο σύνδεση στο API της Eurostat)"""
import json, urllib.request
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
def get(ds, q):
    d = json.load(urllib.request.urlopen(API + ds + "?format=JSON&lang=EN&" + q))
    dims, sz = d["id"], d["size"]
    inv = {k: {v: kk for kk, v in d["dimension"][k]["category"]["index"].items()} for k in dims}
    out = {}
    for f, v in d["value"].items():
        f = int(f); c = []
        for s in reversed(sz): c.append(f % s); f //= s
        c = c[::-1]; out[tuple(inv[dims[i]][c[i]] for i in range(len(dims)))] = v
    return dims, out
CODES = ["TOTAL"] + ["CP%02d" % i for i in range(1, 14)] + ["CP0411", "CP043", "CP044", "CP045", "CP071", "CP072", "CP073"]
dims, raw = get("prc_hicp_minr", "geo=EL&unit=I25&sinceTimePeriod=2019-01&" + "&".join("coicop18=" + c for c in CODES))
idx = {(dict(zip(dims, k))["coicop18"], dict(zip(dims, k))["time"]): v for k, v in raw.items()}
dims, raw = get("prc_hicp_iw", "geo=EL&coicop18=CP12&coicop18=CP13")
iw = {(dict(zip(dims, k))["coicop18"], dict(zip(dims, k))["time"]): v for k, v in raw.items()}
dims, raw = get("hbs_str_t223", "geo=EL&time=2015&time=2020")
hbs = {(dict(zip(dims, k))["time"], dict(zip(dims, k))["quant_inc"], dict(zip(dims, k))["coicop"]): v for k, v in raw.items()}
def yoy(c, t):
    y, m = t.split("-"); return (idx[(c, t)] / idx[(c, f"{int(y)-1}-{m}")] - 1) * 100
def cum(base):
    return lambda c, t: (idx[(c, t)] / (sum(idx[(c, f"{base}-{m:02d}")] for m in range(1, 13)) / 12) - 1) * 100
ITEMS = ["CP01", "CP02", "CP03", "CP041", "CP043", "CP044", "CP045", "CP05", "CP06", "CP071", "CP072", "CP073", "CP08", "CP09", "CP10", "CP11", "CP12"]
MAP = {"CP041": "CP0411"}
def hbs_q(year, t, f):
    res = []
    for q in ["QU1", "QU2", "QU3", "QU4", "QU5"]:
        w = {i: hbs[(year, q, i)] for i in ITEMS}; tot = sum(w.values()); s = 0
        for i, wi in w.items():
            if i == "CP12":  # COICOP 1999 «διάφορα» = COICOP 2018 CP12 + CP13
                a, b = iw[("CP12", t[:4])], iw[("CP13", t[:4])]
                r = (a * f("CP12", t) + b * f("CP13", t)) / (a + b)
            else: r = f(MAP.get(i, i), t)
            s += wi / tot * r
        res.append(round(s, 2))
    return res
# ΕΟΠ 2025, Πίνακας 15 (ΕΛΣΤΑΤ), μερίδια % στις 13 ομάδες COICOP 2018, πεμπτημόρια ισοδύναμης δαπάνης
EOP = [[31.89, 2.08, 3.02, 22.27, 3.98, 8.06, 6.46, 8.07, 0.97, 0.73, 6.55, 1.41, 4.51],
       [29.42, 2.90, 3.75, 19.01, 4.09, 7.03, 9.70, 6.37, 1.17, 1.50, 8.80, 1.63, 4.63],
       [25.35, 3.23, 4.74, 18.21, 4.23, 6.24, 10.38, 5.36, 1.99, 1.87, 11.60, 1.64, 5.16],
       [22.06, 2.92, 5.40, 16.63, 4.17, 5.92, 12.02, 4.94, 2.78, 2.57, 13.52, 1.77, 5.32],
       [13.22, 4.27, 4.88, 11.80, 5.22, 10.42, 16.21, 3.42, 7.57, 3.71, 12.35, 2.37, 4.57]]
def eop_q(t, f):
    return [round(sum(s[i] / sum(s) * f("CP%02d" % (i + 1), t) for i in range(13)), 2) for s in EOP]
def avg2022(c, t): return sum(yoy(c, f"2022-{m:02d}") for m in range(1, 13)) / 12
rows = [("Σεπ 2026, ετήσια", "2026-09", yoy), ("Σεπ 2022, ετήσια", "2022-09", yoy), ("Μ.Ο. 2022, ετήσια", "2022-12", avg2022),
        ("Σεπ 2026 έναντι 2019", "2026-09", cum(2019)), ("Σεπ 2026 έναντι 2020", "2026-09", cum(2020))]
for name, t, f in rows:
    print(name)
    for lab, r in [("  ΕΟΠ 2015 (εισόδημα)", hbs_q("2015", t, f)), ("  ΕΟΠ 2020 (εισόδημα)", hbs_q("2020", t, f)), ("  ΕΟΠ 2025 (δαπάνη)  ", eop_q(t, f))]:
        print(lab, r, " 1ο−5ο:", round(r[0] - r[4], 2))
