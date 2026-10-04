"""usage: analyze.py 'results/synth48_w*.jsonl' [out.md]"""
import sys, glob, json, collections, numpy as np
rows = [json.loads(l) for f in sorted(glob.glob(sys.argv[1])) for l in open(f)]
order = ["clean", "20", "12", "8", "5"]
def ok(p, t, keys): return p is not None and all(p.get(k) == t.get(k) for k in keys)
def feats(r):
    alts = r["con_alts"]; top = alts[0]; sc0 = top[2]
    other = [a[2] for a in alts[1:] if a[1].get("price") != top[1].get("price") or a[1].get("crop") != top[1].get("crop")]
    margin = sc0 - max(other) if other else 10.0           # log-prob gap to best alternative with a different crop/price
    gap = sc0 - (r["lp_free"] if r["lp_free"] is not None else sc0)   # constrained vs unconstrained likelihood (<=0 typically; very negative = audio does not fit grammar)
    return margin, gap
L = []; P = L.append
by = collections.defaultdict(list)
for r in rows: by[r["cond"]].append(r)
P("| channel (SIMULATED FM, CNR) | n | free ASR + fuzzy parser: crop | price exact | crop AND price | closed-grammar decoder: crop | price exact | crop AND price |\n|---|---|---|---|---|---|---|---|")
tot = {}
for c in order:
    if c not in by: continue
    R = by[c]; n = len(R); tot[c] = {}
    cells = []
    for name, key in (("free", "free_parse"), ("con", "con_parse")):
        a = sum(ok(r[key], r["truth"], ["crop"]) for r in R); b = sum(ok(r[key], r["truth"], ["price"]) for r in R); d = sum(ok(r[key], r["truth"], ["crop", "price"]) for r in R)
        cells += ["%d/%d (%.0f%%)" % (x, n, 100*x/n) for x in (a, b, d)]; tot[c][name] = d
    P("| %s | %d | %s |" % ("clean audio, no channel" if c == "clean" else "%s dB" % c, n, " | ".join(cells)))
# unit and place too (constrained, all conditions pooled)
allr = [r for c in order for r in by.get(c, [])]
for key in ("place", "unit"):
    k = sum(ok(r["con_parse"], r["truth"], [key]) for r in allr); P("")
    P("Closed-grammar decoder, %s correct, all conditions pooled: %d/%d (%.0f%%)" % (key, k, len(allr), 100*k/len(allr)))
# abstain analysis (constrained): margin & gap thresholds, calibrate on even-numbered sentences, report on odd
P("\n**Abstain analysis (closed-grammar decoder, all channel conditions pooled).** Rule: accept only if margin >= m (log-prob gap to the best alternative with a different crop or price); otherwise 'not sure, ask a person'. m is chosen on the even-numbered sentences (target: fewest accepted-but-wrong) and reported on the odd-numbered ones.")
cal = [r for r in allr if int(r["id"][1:]) % 2 == 0]; tst = [r for r in allr if int(r["id"][1:]) % 2 == 1]
def stats(rs, m):
    acc = [r for r in rs if feats(r)[0] >= m]; wrong = sum(not ok(r["con_parse"], r["truth"], ["crop", "price"]) for r in acc)
    return len(acc), wrong
P("\n| margin m | calibration set: accepted / wrong-accepted (of %d) | held-out set: accepted / wrong-accepted (of %d) |\n|---|---|---|" % (len(cal), len(tst)))
for m in (0, 0.5, 1, 2, 3, 4, 6):
    a, w = stats(cal, m); a2, w2 = stats(tst, m)
    P("| %.1f | %d / %d | %d / %d |" % (m, a, w, a2, w2))
wrong_all = sum(not ok(r["con_parse"], r["truth"], ["crop", "price"]) for r in allr)
P("\nWithout abstaining, the closed-grammar decoder gives a wrong crop-or-price on %d of %d clips pooled over conditions." % (wrong_all, len(allr)))
txt = "\n".join(L); print(txt)
if len(sys.argv) > 2: open(sys.argv[2], "w").write(txt + "\n")
