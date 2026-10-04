"""Builds results/elfu/summary.md: diagnosis + before/after for the 'dropped thousands' investigation. SYNTHETIC audio for A and B; REAL RFI speech for C."""
import json, glob, sys, subprocess
sys.path.insert(0, "src"); sys.path.insert(0, "eval")
from grammar import parse_sentence
def ok(p, t): return p is not None and p.get("crop") == t.get("crop") and p.get("price") == t.get("price")
D = [json.loads(l) for l in open("results/elfu/diag_waxal12.jsonl")]
wrong = [d for d in D if d["dec"].strip() != None and not ok(parse_sentence(d["dec"].split()), json.load(open("results/gate_synthvoice2/meta.json"))[int(d["id"][1:])-1]["truth"])]
tb = [d["id"] for d in wrong if d["truth_better"]]
E1 = f"Teacher-forced log-likelihood of the TRUTH sentence versus the sentence the baseline beam search returned, voice 2 (WAXAL, SYNTHETIC), 12 dB SIMULATED FM, the {len(wrong)} clips with a wrong crop or price: the truth scored higher in {len(tb)} ({', '.join(tb)}; these are search errors) and LOWER in {len(wrong)-len(tb)} (the recogniser itself prefers the wrong, usually shorter, hypothesis; the dropped-thousands cases are in this group). Typical gap: g16 truth -45.1 over 26 tokens vs decoded -33.3 over 18 tokens."
def fixed(f, meta):
    rows = [json.loads(l) for g in sorted(glob.glob(f)) for l in open(g)]; n = 0; g = 0; ab = []
    for r in rows:
        if r["truth"]: 
            n += 1; g += ok(r["con_parse"], r["truth"])
    return n, g, rows
out = ["### Diagnosis (FACT)", E1, "", "### Variants on cached encoder outputs, all at 12 dB SIMULATED FM (FACT; time-boxed; settings chosen after looking at these same clips, so in-sample)", open("results/elfu/variants_table.md").read(), open("results/elfu/variants_extra.md").read()]
for S, f in (("A voice 1 (SYNTHETIC)", "eval/gate_dryrun/fixed_w*.jsonl"), ("B voice 2 WAXAL (SYNTHETIC)", "results/gate_synthvoice2/fixed_w*.jsonl")):
    n, g, rows = fixed(f, None)
    def margin(r):
        a = r["con_alts"]; top = a[0]; o = [x[2] for x in a[1:] if x[1].get("price") != top[1].get("price") or x[1].get("crop") != top[1].get("crop")]
        return top[2] - max(o) if o else 10.0
    ab = [r for r in rows if not r["truth"] and r["id"] in ("g21", "g22")]
    acc = lambda r: margin(r) >= 2.0 and r["lp_con"] - r["lp_free"] >= -25.0
    A = [r for r in rows if r["truth"] and acc(r)]
    out.append(f"- End-to-end re-run of the gate pipeline with the flagged decoder (`MARKETEAR_DECODER=fixed`, `eval/run_eval.py`, 12 dB only), {S}: crop AND exact price {g}/{n}; demo abstain rule: abstained on {sum(not acc(r) for r in ab)}/{len(ab)} out-of-vocabulary clip(s) (g21/g22); accepted {len(A)} gate clips of which {sum(not ok(r['con_parse'], r['truth']) for r in A)} wrong.")
open("results/elfu/summary.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
