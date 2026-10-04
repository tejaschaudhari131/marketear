"""Swahili number grammar for market prices (0 < n < 1,000,000), word-level.
Grammar (all words lower case):
  D     = moja mbili tatu nne tano sita saba nane tisa              (1-9)
  SM99  = D | kumi | kumi na D | TENS | TENS na D                    (1-99)
  TENS  = ishirini thelathini arobaini hamsini sitini sabini themanini tisini
  NUM   = [laki D] [elfu SM99] [mia D] [SM99]   (at least one part; optional 'na' between parts)
laki = 100,000 (Kenya/Tanzania colloquial), elfu = 1,000, mia = 100.
"""
D = {"moja":1,"mbili":2,"tatu":3,"nne":4,"tano":5,"sita":6,"saba":7,"nane":8,"tisa":9}
TENS = {"ishirini":20,"thelathini":30,"arobaini":40,"hamsini":50,"sitini":60,"sabini":70,"themanini":80,"tisini":90}
NUMBER_WORDS = set(D)|set(TENS)|{"kumi","mia","elfu","laki","na"}
D_INV = {v:k for k,v in D.items()}; TENS_INV = {v:k for k,v in TENS.items()}

def _sm99(w, i):
    """parse 1..99 starting at w[i]; return (value, next_i) or None"""
    if i >= len(w): return None
    t = w[i]
    if t in D: return D[t], i+1
    if t == "kumi":
        if i+2 < len(w)+0 and i+1 < len(w) and w[i+1] == "na" and i+2 < len(w) and w[i+2] in D:
            return 10 + D[w[i+2]], i+3
        return 10, i+1
    if t in TENS:
        if i+2 < len(w) and w[i+1] == "na" and w[i+2] in D:
            return TENS[t] + D[w[i+2]], i+3
        return TENS[t], i+1
    return None

def parse(words):
    """words -> int, or None if the whole sequence is not a valid number."""
    w = list(words); i = 0; total = 0; parts = 0; stage = 0   # stage: 1 laki, 2 elfu, 3 mia, 4 tail
    def skip_na(i):
        # 'na' joins two parts; only skip if a part follows
        return i+1 if i < len(w) and w[i] == "na" and i+1 < len(w) and parts > 0 else i
    while i < len(w):
        i = skip_na(i)
        if i >= len(w): return None
        t = w[i]
        if t == "laki" and stage < 1:
            if i+1 < len(w) and w[i+1] in D: total += 100000*D[w[i+1]]; i += 2; stage = 1; parts += 1; continue
            return None
        if t == "elfu" and stage < 2:
            r = _sm99(w, i+1)
            if r: total += 1000*r[0]; i = r[1]; stage = 2; parts += 1; continue
            return None
        if t == "mia" and stage < 3:
            if i+1 < len(w) and w[i+1] in D: total += 100*D[w[i+1]]; i += 2; stage = 3; parts += 1; continue
            return None
        if stage < 4 and t not in ("laki","elfu","mia","na"):
            r = _sm99(w, i)
            if r: total += r[0]; i = r[1]; stage = 4; parts += 1; continue
            return None
        return None
    return total if parts else None

def _sm99_words(n):
    if n < 10: return [D_INV[n]]
    if n == 10: return ["kumi"]
    if n < 20: return ["kumi","na",D_INV[n-10]]
    t, u = divmod(n, 10)
    return [TENS_INV[t*10]] + (["na", D_INV[u]] if u else [])

def say(n, na_style="all"):
    """int -> list of words. na_style 'all': 'na' before every later part; 'last': only before the final part; 'none'."""
    assert 0 < n < 1_000_000
    parts = []
    l, r = divmod(n, 100000); e, r = divmod(r, 1000); m, t = divmod(r, 100)
    if l: parts.append(["laki", D_INV[l]])
    if e: parts.append(["elfu"] + _sm99_words(e))
    if m: parts.append(["mia", D_INV[m]])
    if t: parts.append(_sm99_words(t))
    out = []
    for k, p in enumerate(parts):
        if k > 0 and (na_style == "all" or (na_style == "last" and k == len(parts)-1)): out.append("na")
        out += p
    return out

if __name__ == "__main__":
    import random
    for n in [5, 15, 85, 100, 250, 1200, 5200, 5300, 12500, 85000, 102500, 265000, 999999]:
        for st in ("all","last","none"):
            w = say(n, st); assert parse(w) == n, (n, st, w, parse(w))
        print(n, " ".join(say(n)), "|", " ".join(say(n,"last")))
    random.seed(0); bad = 0; tot = 0
    for _ in range(20000):
        n = random.randint(1, 999999); st = random.choice(["all","last","none"]); tot += 1
        bad += parse(say(n, st)) != n   # inherent ambiguity, e.g. 'elfu ishirini na mbili' (22,000 vs 20,002)
    print("round-trip mismatches (inherent 'na' ambiguity): %d of %d" % (bad, tot))
    # prices that are multiples of 50 below 400,000 (what a bulletin reads) must round-trip in every style
    for n in range(50, 400000, 50):
        for st in ("all","last","none"):
            assert parse(say(n, st)) == n, (n, st, say(n, st))
    assert parse(["elfu"]) is None and parse(["na","tano"]) is None and parse(["tano","elfu"]) is None
    print("ok: all multiples of 50 in [50, 400000) round-trip in 3 styles")
