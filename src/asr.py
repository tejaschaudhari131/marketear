"""Recognisers on top of PaschalK/whisper-swahili-small (HF, fp32, CPU):
  free_decode()        -> unconstrained text (baseline 'free ASR')
  constrained_decode() -> beam search restricted to the closed price-sentence grammar (our closed-vocabulary route)
Confidence features come from teacher-forced log-likelihoods."""
import torch, numpy as np, time
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from grammar import build_sentence_nfa, Walker, parse_sentence
torch.set_num_threads(1)   # box is shared and oversubscribed: 1 thread/process is 3x faster than 4 here; run several processes instead
MID = "PaschalK/whisper-swahili-small"
class Rec:
    def __init__(self):
        self.proc = WhisperProcessor.from_pretrained(MID); self.m = WhisperForConditionalGeneration.from_pretrained(MID).eval()
        self.tok = self.proc.tokenizer; self.eos = self.tok.eos_token_id
        self.enc = lambda w: self.tok.encode(" "+w, add_special_tokens=False)
        n, end = build_sentence_nfa(self.enc); self.walker = Walker(n, end)
        self.nots = self.tok.convert_tokens_to_ids("<|notimestamps|>")
        self.prompt = [self.tok.convert_tokens_to_ids(t) for t in ("<|startoftranscript|>", "<|sw|>", "<|transcribe|>", "<|notimestamps|>")]
    def feats(self, a16):
        return self.proc.feature_extractor(a16, sampling_rate=16000, return_tensors="pt").input_features
    def encode(self, f):
        with torch.no_grad(): return self.m.model.encoder(f)
    def _gen(self, eo, **kw):
        with torch.no_grad():
            return self.m.generate(encoder_outputs=eo, language="sw", task="transcribe", return_dict_in_generate=True, **kw)
    def free_decode(self, f):
        o = self._gen(f, num_beams=1, do_sample=False, max_new_tokens=60)
        return self.tok.decode(o.sequences[0], skip_special_tokens=True).strip().lower()
    def constrained_decode(self, eo, beams=4, topk=4, max_tokens=45, len_bonus=0.0):
        """own beam search with KV cache; every step restricted to tokens the grammar allows. returns [(text, token_ids_with_prompt, sum_logprob)]"""
        from transformers import EncoderDecoderCache, DynamicCache
        H = eo.last_hidden_state; dec = self.m.model.decoder
        cache = EncoderDecoderCache(DynamicCache(config=self.m.config), DynamicCache(config=self.m.config))
        live = [((), 0.0)]; done = []; last_in = torch.tensor([self.prompt]); first = True
        with torch.no_grad():
            for _ in range(max_tokens):
                B = len(live)
                out = dec(input_ids=last_in, encoder_hidden_states=H.expand(B, -1, -1), past_key_values=cache, use_cache=True)
                lp = torch.log_softmax(self.m.proj_out(out.last_hidden_state[:, -1]).float(), -1).numpy()
                cand = []
                for bi, (p, sc) in enumerate(live):
                    toks, acc = self.walker.allowed(p)
                    for t in toks: cand.append((sc + lp[bi, t] + len_bonus, bi, p + (t,), False))  # len_bonus (default 0 = baseline): per-token bonus used in ranking; reported score is minus the bonus
                    if acc: cand.append((sc + lp[bi, self.eos], bi, p, True))
                cand.sort(key=lambda x: -x[0]); nl = []; idx = []
                for sc, bi, p, fin in cand[:beams]:
                    if fin: done.append((p, sc))
                    else: nl.append((p, sc)); idx.append(bi)
                if not nl: break
                if len(done) >= topk and max(s for _, s in done) > max(s for _, s in nl): break
                cache.reorder_cache(torch.tensor(idx)); live = nl
                last_in = torch.tensor([[p[-1]] for p, _ in live])
        done.sort(key=lambda x: -x[1])
        return [(self.tok.decode(list(p), skip_special_tokens=True).strip().lower(), self.prompt + list(p), float(sc) - len_bonus * len(p)) for p, sc in done[:topk]]
    def loglik(self, eo, ids):
        """sum log P(token | prefix) of generated text tokens (after the 4-token prompt), incl. EOS if present; returns (sum, ntok)"""
        ids = [i for i in ids if i != self.m.config.pad_token_id] if False else ids
        # strip leading decoder_start duplicates: generate output starts with prompt tokens
        k = len(ids) - 1 - ids[::-1].index(self.nots) if self.nots in ids else 3
        txt = ids[k+1:]
        if not txt or txt[-1] != self.eos: txt = txt + [self.eos]
        dec = torch.tensor([self.prompt + txt])
        with torch.no_grad():
            lg = self.m(encoder_outputs=eo, decoder_input_ids=dec[:, :-1]).logits[0]
        lp = torch.log_softmax(lg.float(), -1)
        tgt = dec[0, 1:]; sel = lp[torch.arange(len(tgt)), tgt][len(self.prompt)-1:]
        return float(sel.sum()), len(sel)

    def constrained_decode_fixed(self, eo, alpha=0.75, beams=16, topk=16):
        """EXPERIMENTAL decoder (flag MARKETEAR_DECODER=fixed; baseline stays constrained_decode): the grammar REQUIRES a unit ('kwa <unit>'), the
        16-best list is re-ranked by log-lik + alpha per token (counters the bias towards short numbers that drop 'elfu'). Reported scores are the raw log-liks."""
        if not hasattr(self, "_unit_walker"):
            n, end = build_sentence_nfa(self.enc, require_unit=True); self._unit_walker = Walker(n, end)
        saved = self.walker; self.walker = self._unit_walker
        try: c = self.constrained_decode(eo, beams=beams, topk=topk)
        finally: self.walker = saved
        return sorted(c, key=lambda h: -(h[2] + alpha * (len(h[1]) - len(self.prompt))))
