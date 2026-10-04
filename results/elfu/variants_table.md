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
