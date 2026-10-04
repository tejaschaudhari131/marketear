"""Market Ear v2 core: audio (16 kHz mono) -> closed-vocabulary decode -> fields -> WFP comparison -> accept / abstain, with a receipt.
Nothing is sent anywhere; the output is a proposal that a person confirms.
Abstain rule (tuned on a small set, see STATUS.md, so optimistic): propose only if (a) crop, place and price were decoded, (b) the best reading beats the best
alternative with a different crop or price by MARGIN_MIN log-prob points, and (c) the grammar-constrained reading is not more than GAP_MIN log-prob points
less likely than the free transcript (a low value means the audio does not fit the closed vocabulary, e.g. an unknown crop or non-price news)."""
import os, numpy as np, subprocess, soundfile as sf
import asr, wfp
from grammar import parse_sentence, UNITS
from fmchannel import fm_chain
MARGIN_MIN = 2.0; GAP_MIN = -25.0
SW_NOT_SURE = "Siwezi kuwa na uhakika - muulize mtu"   # draft Swahili, UNKNOWN until a native speaker checks it
EN_NOT_SURE = "Not sure - ask a person"
CROP_EN = {"maize": "Maize", "beans": "Beans", "rice": "Rice"}; CROP_SW = {"maize": "Mahindi", "beans": "Maharage", "rice": "Mchele"}
UNIT_EN = {"BAG": "bag", "90 KG": "90 kg bag", "100 KG": "100 kg bag", "KG": "per kg", "DEBE": "debe (tin)"}
UNIT_SW = {"BAG": "gunia", "90 KG": "gunia la kilo 90", "100 KG": "gunia la kilo 100", "KG": "kwa kilo", "DEBE": "debe"}
def load_audio(path):
    tmp = "/tmp/_me_in.wav"; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", tmp], check=True)
    a, _ = sf.read(tmp, dtype="float32"); return a
def margin_of(alts):
    top = alts[0]; other = [a for a in alts[1:] if a[1].get("price") != top[1].get("price") or a[1].get("crop") != top[1].get("crop")]
    return top[2] - max(a[2] for a in other) if other else 10.0
def fmt(x): return format(int(round(x)), ",")
def messages(f, w):
    c, p, u, price = f["crop"], f["place"], f["unit"], f["price"]; cur = w.get("currency", "") if w.get("status") == "ok" else ""
    ccy = {"KE": "KES", "TZ": "TZS", "UG": "UGX"}[__import__("grammar").PLACES[p.lower()][1]]
    en = "%s (%s) %s: %s %s heard on the bulletin." % (CROP_EN[c], UNIT_EN[u], p, ccy, fmt(price))
    sw = "%s (%s) %s: %s %s kwenye taarifa." % (CROP_SW[c], UNIT_SW[u], p, ccy, fmt(price))
    if w.get("status") == "ok":
        rng = "%s %s-%s" % (w["currency"], fmt(w["min"]), fmt(w["max"]))
        en += " WFP reference %s (%s to %s, median %s): %s." % (rng, w["from"], w["to"], fmt(w["median"]), {"within": "inside the range", "above": "ABOVE the range", "below": "BELOW the range"}[w["verdict"]])
        sw += " Kiwango cha WFP %s: %s." % (rng, {"within": "ndani ya kiwango", "above": "juu ya kiwango", "below": "chini ya kiwango"}[w["verdict"]])
    else:
        en += " No recent WFP reference for this market, crop and unit."; sw += " Hakuna bei ya kulinganisha ya WFP ya hivi karibuni."
    return en, sw
class MarketEar:
    def __init__(self): self.R = asr.Rec()
    def listen(self, a16, simulate_cnr_db=None, seed=0):
        x = a16 if simulate_cnr_db is None else fm_chain(a16, simulate_cnr_db, seed)
        eo = self.R.encode(self.R.feats(x)); cons = self.R.constrained_decode_fixed(eo) if os.environ.get('MARKETEAR_DECODER') == 'fixed' else self.R.constrained_decode(eo)
        out = {"channel": "direct audio (no radio channel)" if simulate_cnr_db is None else "SIMULATED FM channel, CNR %s dB (software model, not a real radio)" % simulate_cnr_db,
               "seconds_audio": round(len(a16)/16000, 1)}
        if not cons: out.update(decision="abstain", reason="no hypothesis fits the price grammar", sw=SW_NOT_SURE, en=EN_NOT_SURE); return out
        alts = [(t, parse_sentence(t.split()), sc) for t, _, sc in cons]
        free = self.R.free_decode(eo); lf = self.R.loglik(eo, self.R.prompt + self.R.tok.encode(" " + free, add_special_tokens=False))[0] if free else None
        m = margin_of(alts); gap = alts[0][2] - lf if lf is not None else None; f = alts[0][1]
        out.update(free_transcript=free, decoded_text=alts[0][0], fields=f, margin=round(m, 1), gap=None if gap is None else round(gap, 1),
                   alternatives=[{"text": t, "fields": p, "logprob": round(sc, 1)} for t, p, sc in alts[1:3]])
        why = None
        if any(f[k] is None for k in ("crop", "place", "price")): why = "crop, place or price could not be read from the decoded sentence"
        elif gap is not None and gap < GAP_MIN: why = "the audio does not fit the closed vocabulary (the free transcript is far more likely: gap %.1f < %.1f)" % (gap, GAP_MIN)
        elif m < MARGIN_MIN: why = "another crop or price fits the audio almost as well (margin %.1f < %.1f)" % (m, MARGIN_MIN)
        if why: out.update(decision="abstain", reason=why, sw=SW_NOT_SURE, en=EN_NOT_SURE); return out
        w = wfp.compare(f["place"], f["crop"], f["unit"], f["price"]); out["wfp"] = w; out["decision"] = "propose"
        out["en"], out["sw"] = messages(f, w); return out
