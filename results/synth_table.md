| channel (SIMULATED FM, CNR) | n | free ASR + fuzzy parser: crop | price exact | crop AND price | closed-grammar decoder: crop | price exact | crop AND price |
|---|---|---|---|---|---|---|---|
| clean audio, no channel | 9 | 9/9 (100%) | 6/9 (67%) | 6/9 (67%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| 20 dB | 8 | 8/8 (100%) | 6/8 (75%) | 6/8 (75%) | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) |
| 12 dB | 7 | 7/7 (100%) | 5/7 (71%) | 5/7 (71%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| 8 dB | 6 | 6/6 (100%) | 5/6 (83%) | 5/6 (83%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |
| 5 dB | 6 | 6/6 (100%) | 4/6 (67%) | 4/6 (67%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |

Closed-grammar decoder, place correct, all conditions pooled: 35/36 (97%)

Closed-grammar decoder, unit correct, all conditions pooled: 36/36 (100%)

**Abstain analysis (closed-grammar decoder, all channel conditions pooled).** Rule: accept only if margin >= m (log-prob gap to the best alternative with a different crop or price); otherwise 'not sure, ask a person'. m is chosen on the even-numbered sentences (target: fewest accepted-but-wrong) and reported on the odd-numbered ones.

| margin m | calibration set: accepted / wrong-accepted (of 19) | held-out set: accepted / wrong-accepted (of 17) |
|---|---|---|
| 0.0 | 19 / 0 | 17 / 0 |
| 0.5 | 19 / 0 | 17 / 0 |
| 1.0 | 19 / 0 | 17 / 0 |
| 2.0 | 19 / 0 | 17 / 0 |
| 3.0 | 19 / 0 | 17 / 0 |
| 4.0 | 19 / 0 | 17 / 0 |
| 6.0 | 18 / 0 | 13 / 0 |

Without abstaining, the closed-grammar decoder gives a wrong crop-or-price on 0 of 36 clips pooled over conditions.
