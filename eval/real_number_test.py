"""REAL human broadcast speech (OpenSLR SLR25, RFI Swahili news, test split) containing one number phrase.
Free ASR: unconstrained greedy decode; read the number words it produced.
Closed-number decoder: the words around the number are given (ORACLE frame, from the reference transcript), the number slot is open
(any value < 1,000,000 in our grammar). Measures number recovery on real speech; it does NOT measure the full product."""
import sys, glob, random, json, re, time, numpy as np, soundfile as sf
sys.path.insert(0, "src")
import asr
from fmchannel import fm_chain
from grammar import build_frame_nfa, Walker
from swnum import NUMBER_WORDS, parse
from baseline import snap
N = int(sys.argv[1]); conds = sys.argv[2].split(","); out = sys.argv[3]
base = "data/slr25/data_broadcastnews_sw/data/test/"
def norm(s): s = s.lower(); s = re.sub(r"[^\w\s]", "", s); return re.sub(r"\s+", " ", s).strip()
txt = {l.split(" ", 1)[0]: norm(l.split(" ", 1)[1]) for l in open(base + "text")}
files = {f.split("/")[-1][:-4]: f for f in glob.glob(base + "wav*/*/*.wav")}
cands = []
for k, t in txt.items():
    ws = t.split()
    if k not in files or not (4 <= len(ws) <= 25): continue
    runs = []; i = 0
    while i < len(ws):
        if ws[i] in NUMBER_WORDS and ws[i] != "na":
            j = i
            while j < len(ws) and ws[j] in NUMBER_WORDS: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    if len(runs) != 1: continue
    i, j = runs[0]; run = ws[i:j]
    v = parse(run)
    if v is None or v == 0: continue
    cands.append((k, ws[:i], run, v, ws[j:]))
random.seed(5); random.shuffle(cands); sel = []
for c in cands:
    a, sr = sf.read(files[c[0]], dtype="float32")
    if 2 <= len(a)/sr <= 14: sel.append((c, a))
    if len(sel) == N: break
print("candidates with exactly one parseable number phrase:", len(cands), "| using", len(sel), flush=True)
R = asr.Rec(); fo = open(out, "a")
for k, (c, a) in enumerate(sel):
    key, pre, run, val, suf = c
    enc = R.enc; nfa, end = build_frame_nfa(enc, " ".join(pre), " ".join(suf)); saved = R.walker; R.walker = Walker(nfa, end)
    for cnd in conds:
        x = a if cnd == "clean" else fm_chain(a, float(cnd), seed=k*7+int(float(cnd)))
        eo = R.encode(R.feats(x)); fr = R.free_decode(eo)
        ws = [snap(w) for w in fr.split()]
        rn = []; i = 0; best = None
        while i < len(ws):
            if ws[i] in NUMBER_WORDS and ws[i] != "na":
                j = i
                while j < len(ws) and ws[j] in NUMBER_WORDS: j += 1
                r_ = ws[i:j]
                while r_ and r_[-1] == "na": r_ = r_[:-1]
                v = parse(r_)
                if v is not None and (best is None or len(r_) > best[0]): best = (len(r_), v)
                i = j
            else: i += 1
        cons = R.constrained_decode(eo)
        cv = None
        if cons:
            t0 = cons[0][0].split(); a0 = len(pre); cv = parse(t0[a0:len(t0)-len(suf)] if suf else t0[a0:])
        fo.write(json.dumps({"id": key, "cond": cnd, "ref": " ".join(pre + run + suf), "truth": val, "free_text": fr, "free_value": best[1] if best else None, "con_text": cons[0][0] if cons else None, "con_value": cv}, ensure_ascii=False) + "\n"); fo.flush()
    R.walker = saved
