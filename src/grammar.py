"""Closed-vocabulary price-sentence grammar (word-level) + token-level NFA for constrained decoding.
FACT: vocabulary is deliberately tiny: 3 crops, 16 places, 6 unit phrases, ~20 function/number words.
"""
import itertools
from swnum import D, TENS, parse as parse_num

CROPS = {"mahindi":"maize", "maharage":"beans", "mchele":"rice"}
PLACES = {  # spoken form -> (canonical name, country)
    "kisumu":("Kisumu","KE"), "nakuru":("Nakuru","KE"), "eldoret":("Eldoret","KE"), "kitale":("Kitale","KE"),
    "nairobi":("Nairobi","KE"), "mombasa":("Mombasa","KE"), "kakamega":("Kakamega","KE"), "kisii":("Kisii","KE"),
    "dodoma":("Dodoma","TZ"), "arusha":("Arusha","TZ"), "mwanza":("Mwanza","TZ"), "mbeya":("Mbeya","TZ"),
    "morogoro":("Morogoro","TZ"), "dar es salaam":("Dar es Salaam","TZ"), "kampala":("Kampala","UG"), "gulu":("Gulu","UG"),
}
UNITS = {  # spoken phrase -> canonical unit label (None = no WFP-comparable unit)
    "gunia":"BAG", "gunia la kilo tisini":"90 KG", "gunia la kilo mia moja":"100 KG",
    "kilo":"KG", "kilo moja":"KG", "debe":"DEBE",
}
FUNCTION_WORDS = ["bei","ya","leo","ni","shilingi","sokoni","kwa","la"]

# ---------------- tiny NFA combinators ----------------
class NFA:
    def __init__(self): self.edges = [[]]    # state -> list of (label|None, dst)
    def new(self): self.edges.append([]); return len(self.edges)-1
    def add(self, a, lab, b): self.edges[a].append((lab, b))

def _word(n, toks, a):           # chain of token edges; returns end state
    for t in toks:
        b = n.new(); n.add(a, t, b); a = b
    return a

class Frag:   # a fragment builder: build(n, start) -> end
    def __init__(self, f): self.f = f
    def build(self, n, a): return self.f(n, a)

def W(words, enc):
    toks = [t for w in words.split() for t in enc(w)]
    return Frag(lambda n, a: _word(n, toks, a))
def Seq(*fs): 
    def f(n, a):
        for x in fs: a = x.build(n, a)
        return a
    return Frag(f)
def Alt(*fs):
    def f(n, a):
        end = n.new()
        for x in fs:
            s = n.new(); n.add(a, None, s); e = x.build(n, s); n.add(e, None, end)
        return end
    return Frag(f)
def Opt(x): return Alt(x, Seq())

def number_frag(w):
    Dg = Alt(*[w(k) for k in D])
    SM = Alt(Dg, w("kumi"), Seq(w("kumi na"), Dg), Alt(*[w(k) for k in TENS]), Seq(Alt(*[w(k) for k in TENS]), w("na"), Dg))
    LAKI = Seq(w("laki"), Dg); ELFU = Seq(w("elfu"), SM); MIA = Seq(w("mia"), Dg); TAIL = SM
    parts = [LAKI, ELFU, MIA, TAIL]; alts = []
    for r in range(1, 5):
        for sub in itertools.combinations(range(4), r):
            seq = []
            for k, i in enumerate(sub):
                if k: seq.append(Opt(w("na")))
                seq.append(parts[i])
            alts.append(Seq(*seq))
    return Alt(*alts)

def build_frame_nfa(enc, prefix, suffix):
    """real-speech number test: known words before/after (oracle frame) + an OPEN number slot (any value < 1,000,000 in the grammar)"""
    w = lambda s: W(s, enc)
    S = Seq(w(prefix) if prefix else Seq(), number_frag(w), w(suffix) if suffix else Seq())
    n = NFA(); end = S.build(n, 0); return n, end

def build_sentence_nfa(enc, crops=CROPS, places=PLACES, units=UNITS, require_unit=False):  # require_unit=False is the baseline; True is an experiment flag
    w = lambda s: W(s, enc)
    Dg = Alt(*[w(k) for k in D])
    SM = Alt(Dg, w("kumi"), Seq(w("kumi na"), Dg), Alt(*[w(k) for k in TENS]), Seq(Alt(*[w(k) for k in TENS]), w("na"), Dg))
    LAKI = Seq(w("laki"), Dg); ELFU = Seq(w("elfu"), SM); MIA = Seq(w("mia"), Dg); TAIL = SM
    parts = [LAKI, ELFU, MIA, TAIL]; alts = []
    for r in range(1, 5):
        for sub in itertools.combinations(range(4), r):
            seq = []
            for k, i in enumerate(sub):
                if k: seq.append(Opt(w("na")))
                seq.append(parts[i])
            alts.append(Seq(*seq))
    NUM = Alt(*alts)
    CROP = Alt(*[w(k) for k in crops]); PLACE = Alt(*[w(k) for k in places])
    UNIT = Seq(w("kwa"), Alt(*[w(k) for k in units]))
    PRICE = Seq(w("ni"), Opt(w("shilingi")), NUM, Opt(w("shilingi")), UNIT if require_unit else Opt(UNIT))
    A = Seq(Opt(w("bei ya")), CROP, Opt(w("sokoni")), PLACE, Opt(w("leo")), PRICE)
    B = Seq(PLACE, Opt(w("leo")), w("bei ya"), CROP, PRICE)
    S = Alt(A, B)
    n = NFA(); end = S.build(n, 0)
    return n, end

class Walker:
    """simulate the NFA on a token prefix"""
    def __init__(self, nfa, end):
        self.n, self.end = nfa, end; self.cache = {}
        self.eps = {}
    def closure(self, states):
        st = set(states); stack = list(states)
        while stack:
            s = stack.pop()
            for lab, d in self.n.edges[s]:
                if lab is None and d not in st: st.add(d); stack.append(d)
        return frozenset(st)
    def start(self): return self.closure({0})
    def step(self, states, tok):
        nxt = {d for s in states for lab, d in self.n.edges[s] if lab == tok}
        return self.closure(nxt) if nxt else frozenset()
    def state_after(self, prefix):
        prefix = tuple(prefix)
        if prefix in self.cache: return self.cache[prefix]
        if not prefix: r = self.start()
        else: r = self.step(self.state_after(prefix[:-1]), prefix[-1])
        self.cache[prefix] = r; return r
    def allowed(self, prefix):
        st = self.state_after(prefix)
        toks = {lab for s in st for lab, d in self.n.edges[s] if lab is not None}
        return toks, (self.end in st)

# ---------------- text -> fields ----------------
def parse_sentence(words):
    """words (list of str) -> dict(crop, place, price, unit) ; fields None when absent/invalid"""
    ws = list(words); text = " ".join(ws)
    crop = next((CROPS[w] for w in ws if w in CROPS), None)
    place = None
    for p in sorted(PLACES, key=lambda x: -len(x)):
        if (" "+p+" ") in (" "+text+" "): place = PLACES[p][0]; break
    price = None; unit = None
    if "ni" in ws:
        i = ws.index("ni")+1; j = len(ws)
        if "kwa" in ws[i:]: j = ws.index("kwa", i)
        body = [x for x in ws[i:j] if x != "shilingi"]
        price = parse_num(body)
        if j < len(ws):
            u = " ".join(ws[j+1:]); unit = UNITS.get(u)
    return {"crop":crop, "place":place, "price":price, "unit":unit}

if __name__ == "__main__":
    from transformers import WhisperTokenizer
    tok = WhisperTokenizer.from_pretrained("PaschalK/whisper-swahili-small")
    enc = lambda w: tok.encode(" "+w, add_special_tokens=False)
    n, end = build_sentence_nfa(enc); wk = Walker(n, end)
    print("NFA states:", len(n.edges))
    for s in ["bei ya mahindi kisumu leo ni shilingi elfu tano na mia mbili kwa gunia", "kisumu bei ya maharage ni mia tatu kwa kilo", "bei ya mchele dar es salaam ni elfu mbili na mia tano kwa kilo moja"]:
        ids = [t for w in s.split() for t in enc(w)]
        st = wk.state_after(ids); print(s, "->", end in st, parse_sentence(s.split()))
        # also check every prefix allows the next token
        for i in range(len(ids)):
            toks, _ = wk.allowed(ids[:i]); assert ids[i] in toks, (s, i)
    print("tokenisation:", [tok.decode([t]) for t in enc("mahindi")], [tok.decode([t]) for t in enc("themanini")])
