"""Score decoder variants on sets A, B (SYNTHETIC; crop AND exact price at 12 dB SIMULATED FM) and C (REAL RFI speech; exact number, oracle frame, 12 dB)."""
import json, glob, sys, math
sys.path.insert(0, "src")
from grammar import parse_sentence
from swnum import parse
def load(S): return [json.loads(l) for f in sorted(glob.glob(f"results/elfu/var_{S}_w*.jsonl")) for l in open(f)]
def correct(S, r, text):
    if S == "C":
        t = text.split(); a = len(r["pre"]); return parse(t[a:len(t)-len(r["suf"])] if r["suf"] else t[a:]) == r["truth"]
    p = parse_sentence(text.split()); T = r["truth"]; return p["crop"] == T["crop"] and p["price"] == T["price"]
def pick(nb, mode, alpha=0.0):
    if not nb: return None
    if mode == "raw": key = lambda h: h[1]
    elif mode == "bonus": key = lambda h: h[1] + alpha * h[2]
    elif mode == "norm": key = lambda h: h[1] / max(h[2], 1)
    return max(nb, key=key)[0]
VARIANTS = [("baseline: beams 4, raw log-lik (what the gate used)", "base", "raw", 0), ("beams 16 (wider beam only)", "b16", "raw", 0)]
VARIANTS += [(f"beams 16 N-best, rerank raw + {a} per token", "b16", "bonus", a) for a in (0.25, 0.5, 0.75, 1.0, 1.5)]
VARIANTS += [("beams 16 N-best, rerank by log-lik / tokens", "b16", "norm", 0), ("grammar REQUIRES a unit, beams 16", "unit16", "raw", 0)]
VARIANTS += [(f"grammar requires unit + rerank +{a} per token", "unit16", "bonus", a) for a in (0.25, 0.5, 0.75, 1.0)]
D = {S: load(S) for S in "ABC"}
L = ["| variant | A: voice 1 (SYNTHETIC) /20 | B: voice 2 WAXAL (SYNTHETIC) /20 | C: REAL RFI numbers /20 | A+B+C of 60 |", "|---|---|---|---|---|"]
res = {}
for name, key, mode, al in VARIANTS:
    row = []
    for S in "ABC":
        k2 = key.replace('unit16', 'b16') if S == 'C' else key   # set C has no unit slot: the unit flag does not apply, same decoder as b16
        rs = [r for r in D[S] if k2 in r]
        row.append((sum(correct(S, r, pick(r[k2], mode, al) or "") for r in rs), len(rs)))
    res[name] = row
    L.append(f"| {name} | " + " | ".join(f"{c}/{n}" for c, n in row) + f" | {sum(c for c, _ in row)} |")
open("results/elfu/variants_table.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))

# oracle: is a correct hypothesis anywhere in the 16-best list?
O = []
for S in "AB":
    rs = [r for r in D[S] if "b16" in r]; O.append(f"set {S}: correct hypothesis present in the 16-best list for {sum(any(correct(S, r, h[0]) for h in r['b16']) for r in rs)}/{len(rs)} clips")
# padding / normalisation experiment
P = ["| set | " + " | ".join(["none", "pad0.5", "pad1.0", "norm", "pad1.0+norm"]) + " |", "|---|---|---|---|---|---|"]
for S in "AB":
    rs = [json.loads(l) for f in glob.glob(f"results/elfu/pad_{S}.jsonl") for l in open(f)]
    if not rs: continue
    P.append(f"| {S} ({len(rs)} clips, baseline decoder) | " + " | ".join(str(sum(correct(S, {'truth': r['truth']}, (r[v][0][0] if r[v] else '')) for r in rs)) for v in ["none", "pad0.5", "pad1.0", "norm", "pad1.0+norm"]) + " |")
open("results/elfu/variants_extra.md", "w").write("\n".join(O) + "\n\n" + "\n".join(P) + "\n"); print("\n".join(O)); print("\n".join(P))
