"""WFP reference-price lookup (HDX WFP Food Prices, CC BY-IGO). Reads the three CSVs in data/. Window = 24 months ending at the newest row."""
import pandas as pd, os
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")
CCY = {"KE": "KES", "TZ": "TZS", "UG": "UGX"}
CROP_NAMES = {"maize": ["Maize", "Maize (white)", "Maize (white, dry)"], "beans": ["Beans", "Beans (dry)", "Beans (rosecoco)", "Beans (yellow)", "Beans (spotted)"], "rice": ["Rice", "Rice (aromatic)"]}
# spoken place -> WFP market names (exact strings in the CSVs) ; chosen by hand from the market lists, see docs/WFP_COVERAGE.md
PLACE_MARKETS = {
 "Kisumu": ("KE", ["Kibuye (Kisumu)", "Kisumu"]), "Nakuru": ("KE", ["Nakuru", "Wakulima (Nakuru)"]), "Eldoret": ("KE", ["Eldoret town (Uasin Gishu)"]),
 "Kitale": ("KE", ["Kitale"]), "Nairobi": ("KE", ["Nairobi", "Kangemi (Nairobi)", "Wakulima (Nairobi)"]), "Mombasa": ("KE", ["Mombasa", "Kongowea (Mombasa)"]),
 "Kakamega": ("KE", ["Kakamega"]), "Kisii": ("KE", ["Kisii"]),
 "Dodoma": ("TZ", ["Dodoma (Majengo)"]), "Arusha": ("TZ", ["Arusha (urban)"]), "Mwanza": ("TZ", ["Mwanza"]), "Mbeya": ("TZ", ["Mbeya (SIDO)"]),
 "Morogoro": ("TZ", ["Morogoro"]), "Dar es Salaam": ("TZ", ["Ilala (Buguruni)", "Kinondoni (Tandale)", "Temeke (Tandika)", "Mwananyamala"]),
 "Kampala": ("UG", ["Owino", "Kampala"]), "Gulu": ("UG", ["Gulu"]),
}
BAG_DEFAULT = {"KE": "90 KG", "TZ": "100 KG", "UG": None}
_DB = None
def db():
    global _DB
    if _DB is None:
        fr = []
        for c in ("ken", "tza", "uga"):
            d = pd.read_csv(os.path.join(DATA, f"wfp_{c}.csv"), skiprows=[1], parse_dates=["date"]); d["cc"] = {"ken": "KE", "tza": "TZ", "uga": "UG"}[c]; fr.append(d)
        _DB = pd.concat(fr, ignore_index=True)
    return _DB
def reference(place, crop, unit, months=24, min_obs=6):
    """-> dict(status in {'ok','no_reference'}, ...). unit in {'KG','90 KG','100 KG','BAG','DEBE', None}"""
    if place not in PLACE_MARKETS: return {"status": "no_reference", "why": "place not in the market list"}
    cc, mk = PLACE_MARKETS[place]; assumed = None
    if unit == "BAG":
        unit = BAG_DEFAULT[cc]; assumed = unit
        if unit is None: return {"status": "no_reference", "why": "bare 'gunia' has no WFP bag size for this country"}
    if unit in (None, "DEBE"): return {"status": "no_reference", "why": "unit has no WFP equivalent (WFP series use KG, 50 KG, 90 KG, 100 KG)"}
    D = db(); end = D.date.max(); start = end - pd.DateOffset(months=months)
    x = D[(D.cc == cc) & (D.market.isin(mk)) & (D.commodity.isin(CROP_NAMES[crop])) & (D.unit == unit) & (D.date > start)]
    if len(x) < min_obs:
        last = D[(D.cc == cc) & (D.market.isin(mk)) & (D.commodity.isin(CROP_NAMES[crop])) & (D.unit == unit)].date.max()
        return {"status": "no_reference", "why": "fewer than %d WFP observations in the last %d months (%d found; last WFP row for this market/crop/unit: %s)" % (min_obs, months, len(x), "none" if pd.isna(last) else last.strftime("%Y-%m"))}
    return {"status": "ok", "currency": CCY[cc], "unit": unit, "assumed_unit": assumed, "min": float(x.price.min()), "median": float(x.price.median()), "max": float(x.price.max()),
            "n": int(len(x)), "from": x.date.min().strftime("%Y-%m"), "to": x.date.max().strftime("%Y-%m"), "markets": sorted(x.market.unique()), "commodities": sorted(x.commodity.unique()), "pricetypes": sorted(x.pricetype.unique())}
def compare(place, crop, unit, price):
    r = reference(place, crop, unit)
    if r["status"] != "ok": return r
    r = dict(r); r["verdict"] = "within" if r["min"] <= price <= r["max"] else ("above" if price > r["max"] else "below"); r["price"] = price
    return r
if __name__ == "__main__":
    import sys; sys.path.insert(0, HERE); from grammar import PLACES, CROPS, UNITS
    L = ["| place | crop | unit | WFP result |", "|---|---|---|---|"]
    for p, (nm, cc) in PLACES.items():
        for crop in ("maize", "beans", "rice"):
            for u in ("KG", "BAG", "90 KG" if cc == "KE" else "100 KG"):
                r = reference(nm, crop, u)
                if u == "BAG" and cc != "KE" and False: continue
                L.append("| %s | %s | %s | %s |" % (nm, crop, u, ("%s %s-%s (median %s, n=%d, %s to %s, %s%s)" % (r["currency"], format(r["min"], ",.0f"), format(r["max"], ",.0f"), format(r["median"], ",.0f"), r["n"], r["from"], r["to"], ", ".join(r["markets"]), "; bag size assumed " + r["assumed_unit"] if r["assumed_unit"] else "")) if r["status"] == "ok" else "NO REFERENCE: " + r["why"]))
    print("\n".join(L))
