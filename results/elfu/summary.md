### Diagnosis (FACT)
Teacher-forced log-likelihood of the TRUTH sentence versus the sentence the baseline beam search returned, voice 2 (WAXAL, SYNTHETIC), 12 dB SIMULATED FM, the 9 clips with a wrong crop or price: the truth scored higher in 3 (g11, g13, g17; these are search errors) and LOWER in 6 (the recogniser itself prefers the wrong, usually shorter, hypothesis; the dropped-thousands cases are in this group). Typical gap: g16 truth -45.1 over 26 tokens vs decoded -33.3 over 18 tokens.

### Variants on cached encoder outputs, all at 12 dB SIMULATED FM (FACT; time-boxed; settings chosen after looking at these same clips, so in-sample)
| variant | A: voice 1 (SYNTHETIC) /20 | B: voice 2 WAXAL (SYNTHETIC) /20 | C: REAL RFI numbers /20 | A+B+C of 60 |
|---|---|---|---|---|
| baseline: beams 4, raw log-lik (what the gate used) | 19/20 | 11/20 | 20/20 | 50 |
| beams 16 (wider beam only) | 19/20 | 11/20 | 20/20 | 50 |
| beams 16 N-best, rerank raw + 0.25 per token | 19/20 | 13/20 | 20/20 | 52 |
| beams 16 N-best, rerank raw + 0.5 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 0.75 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 1.0 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 1.5 per token | 19/20 | 16/20 | 20/20 | 55 |
| beams 16 N-best, rerank by log-lik / tokens | 19/20 | 15/20 | 20/20 | 54 |
| grammar REQUIRES a unit, beams 16 | 19/20 | 16/20 | 20/20 | 55 |
| grammar requires unit + rerank +0.25 per token | 19/20 | 16/20 | 20/20 | 55 |
| grammar requires unit + rerank +0.5 per token | 20/20 | 16/20 | 20/20 | 56 |
| grammar requires unit + rerank +0.75 per token | 20/20 | 16/20 | 20/20 | 56 |
| grammar requires unit + rerank +1.0 per token | 20/20 | 16/20 | 20/20 | 56 |

set A: correct hypothesis present in the 16-best list for 20/20 clips
set B: correct hypothesis present in the 16-best list for 18/20 clips

| set | none | pad0.5 | pad1.0 | norm | pad1.0+norm |
|---|---|---|---|---|---|
| B (8 clips, baseline decoder) | 6 | 5 | 6 | 6 | 6 |

- End-to-end re-run of the gate pipeline with the flagged decoder (`MARKETEAR_DECODER=fixed`, `eval/run_eval.py`, 12 dB only), A voice 1 (SYNTHETIC): crop AND exact price 20/20; demo abstain rule: abstained on 2/2 out-of-vocabulary clip(s) (g21/g22); accepted 19 gate clips of which 0 wrong.
- End-to-end re-run of the gate pipeline with the flagged decoder (`MARKETEAR_DECODER=fixed`, `eval/run_eval.py`, 12 dB only), B voice 2 WAXAL (SYNTHETIC): crop AND exact price 16/20; demo abstain rule: abstained on 2/2 out-of-vocabulary clip(s) (g21/g22); accepted 11 gate clips of which 1 wrong.
