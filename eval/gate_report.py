"""usage: gate_report.py 'WORKDIR/results_w*.jsonl' OUT.md [margin_threshold]"""
import sys, glob, json, collections
sys.path.insert(0, "eval")
rows = [json.loads(l) for f in sorted(glob.glob(sys.argv[1])) for l in open(f)]
m_thr = float(sys.argv[3]) if len(sys.argv) > 3 else None
def ok(p, t): return p is not None and t is not None and p.get("crop") == t.get("crop") and p.get("price") == t.get("price")
def margin(r):
    alts = r["con_alts"]; top = alts[0]
    other = [a[2] for a in alts[1:] if a[1].get("price") != top[1].get("price") or a[1].get("crop") != top[1].get("crop")]
    return top[2] - max(other) if other else 10.0
G = [r for r in rows if r["truth"]]; A = [r for r in rows if not r["truth"] and r["id"] in ("g21", "g22")]
L = ["# GO/NO-GO gate report (simulated FM channel; one speaker, scripted sentences)\n"]
L.append("Pass criterion per sentence: crop AND exact price both correct. Gate: GO if either route reaches >=16 of 20 at 12 dB CNR.\n")
L.append("| condition | free ASR + fuzzy parser | closed-grammar decoder | closed-grammar decoder with abstain (margin >= %s) |\n|---|---|---|---|" % (m_thr if m_thr is not None else "n/a"))
res = {}
for c in ["clean", "20", "12", "8"]:
    R = [r for r in G if r["cond"] == c]
    if not R: continue
    f = sum(ok(r["free_parse"], r["truth"]) for r in R); k = sum(ok(r["con_parse"], r["truth"]) for r in R)
    if m_thr is not None:
        acc = [r for r in R if margin(r) >= m_thr]; ka = sum(ok(r["con_parse"], r["truth"]) for r in acc); w = len(acc) - ka
        cell = "accepted %d, correct %d, wrong-accepted %d, abstained %d" % (len(acc), ka, w, len(R) - len(acc))
    else: cell = "n/a"
    L.append("| %s | %d/%d | %d/%d | %s |" % ("clean (no channel)" if c == "clean" else c + " dB", f, len(R), k, len(R), cell)); res[c] = (f, k, len(R))
if "12" in res:
    f, k, n = res["12"]; go = max(f, k) >= 16 and n >= 20
    L.append("\n**GATE RESULT: %s** (12 dB: free route %d/%d, closed-grammar route %d/%d; threshold 16/20)\n" % ("GO" if go else "NO-GO", f, n, k, n))
else: L.append("\n12 dB results missing: gate not computed.\n")
L.append("\n## Per-sentence detail (closed-grammar decoder)\n\n| id | cond | truth | decoded | ok | margin |\n|---|---|---|---|---|---|")
for r in sorted(G, key=lambda r: (r["cond"], r["id"])):
    t = r["truth"]; p = r["con_parse"] or {}
    L.append("| %s | %s | %s %s %s | %s %s %s | %s | %.1f |" % (r["id"], r["cond"], t["crop"], t["place"], t["price"], p.get("crop"), p.get("place"), p.get("price"), "yes" if ok(p, t) else "NO", margin(r)))
if A:
    L.append("\n## Abstain tests (g21 coffee, g22 weather news; vocabulary does not contain the content)\n\n| id | cond | free text | grammar-forced text | margin | free-vs-constrained loglik gap |\n|---|---|---|---|---|---|")
    for r in sorted(A, key=lambda r: (r["id"], r["cond"])):
        L.append("| %s | %s | %s | %s | %.1f | %.1f |" % (r["id"], r["cond"], r["free_text"], r["con_text"], margin(r), (r["lp_con"] - r["lp_free"]) if r["lp_free"] is not None else float("nan")))
open(sys.argv[2], "w").write("\n".join(L) + "\n"); print("\n".join(L[:12]))
