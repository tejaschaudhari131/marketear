"""Generate synthetic price bulletin sentences from the closed grammar with WFP-plausible price ranges.
Ranges are rough plausibility bands taken from the WFP Kenya/Tanzania/Uganda CSVs (see docs/DATA_TABLE.md); they are for
test material only, not forecasts."""
import random, sys, json
sys.path.insert(0, "src")
from swnum import say, parse
from grammar import CROPS, PLACES, parse_sentence
RANGES = {  # (country, crop, unit_phrase) -> (lo, hi, step)
 ("KE","mahindi","gunia"):(3000,6500,50), ("KE","mahindi","gunia la kilo tisini"):(3000,6500,50),
 ("KE","maharage","gunia"):(8000,16000,100), ("KE","mchele","kilo"):(100,220,5), ("KE","mahindi","kilo"):(40,90,5), ("KE","maharage","kilo"):(120,220,10),
 ("TZ","mahindi","kilo"):(800,1500,50), ("TZ","mchele","kilo"):(2000,3200,50), ("TZ","maharage","kilo"):(2000,3500,50),
 ("TZ","mahindi","gunia la kilo mia moja"):(60000,120000,1000),
 ("UG","mahindi","kilo"):(900,2000,50), ("UG","maharage","kilo"):(2500,4500,100),
}
def gen(n, seed):
    r = random.Random(seed); keys = list(RANGES); out = []
    while len(out) < n:
        cc, crop, unit = r.choice(keys)
        place = r.choice([p for p,(nm,c) in PLACES.items() if c == cc])
        lo, hi, st = RANGES[(cc,crop,unit)]; price = r.randrange(lo, hi+1, st)
        nums = say(price, r.choice(["all","all","last","none"]))
        if parse(nums) != price: continue
        shil = r.random() < 0.7
        body = ["ni"] + (["shilingi"] if shil else []) + nums + ([] if r.random() < 0.15 else ["kwa"] + unit.split())
        if r.random() < 0.7:
            w = (["bei","ya"] if r.random() < 0.8 else []) + [crop] + (["sokoni"] if r.random()<0.15 else []) + place.split() + (["leo"] if r.random()<0.4 else []) + body
        else:
            w = place.split() + (["leo"] if r.random()<0.3 else []) + ["bei","ya",crop] + body
        f = parse_sentence(w)
        out.append({"id": "s%03d" % len(out), "text": " ".join(w), "truth": f})
    return out
if __name__ == "__main__":
    n = int(sys.argv[1]); s = gen(n, int(sys.argv[2])); json.dump(s, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
    for x in s[:8]: print(x["text"], x["truth"])
