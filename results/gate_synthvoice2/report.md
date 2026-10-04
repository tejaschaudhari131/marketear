# GO/NO-GO gate report (simulated FM channel; one speaker, scripted sentences)

Pass criterion per sentence: crop AND exact price both correct. Gate: GO if either route reaches >=16 of 20 at 12 dB CNR.

| condition | free ASR + fuzzy parser | closed-grammar decoder | closed-grammar decoder with abstain (margin >= n/a) |
|---|---|---|---|
| 20 dB | 1/20 | 13/20 | n/a |
| 12 dB | 0/20 | 11/20 | n/a |
| 8 dB | 1/20 | 10/20 | n/a |

**GATE RESULT: NO-GO** (12 dB: free route 0/20, closed-grammar route 11/20; threshold 16/20)


## Per-sentence detail (closed-grammar decoder)

| id | cond | truth | decoded | ok | margin |
|---|---|---|---|---|---|
| g01 | 12 | maize Kisumu 5200 | maize Kisumu 5400 | NO | 2.0 |
| g02 | 12 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 10.3 |
| g03 | 12 | rice Nairobi 160 | rice Nairobi 160 | yes | 6.9 |
| g04 | 12 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 1.0 |
| g05 | 12 | beans Kitale 220 | beans Kitale 220 | yes | 12.4 |
| g06 | 12 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 1.2 |
| g07 | 12 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 3.5 |
| g08 | 12 | beans Arusha 3500 | beans Arusha 23 | NO | 3.1 |
| g09 | 12 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 4.5 |
| g10 | 12 | maize Morogoro 74000 | maize Morogoro 84 | NO | 2.3 |
| g11 | 12 | maize Kakamega 3800 | maize Kakamega 32 | NO | 10.1 |
| g12 | 12 | rice Mombasa 190 | rice Mombasa 190 | yes | 6.8 |
| g13 | 12 | beans Kisii 9500 | beans Kisii 309 | NO | 11.7 |
| g14 | 12 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 4.9 |
| g15 | 12 | maize Gulu 1500 | maize Gulu 1100 | NO | 2.1 |
| g16 | 12 | rice Dar es Salaam 2800 | rice Dar es Salaam 80 | NO | 5.0 |
| g17 | 12 | beans Dodoma 3000 | maize Mbeya 4 | NO | 0.2 |
| g18 | 12 | maize Kampala 1800 | maize Mbeya 1800 | yes | 4.3 |
| g19 | 12 | beans Mwanza 250000 | beans Mwanza 2 | NO | 10.0 |
| g20 | 12 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 9.1 |
| g01 | 20 | maize Kisumu 5200 | maize Kisumu 5400 | NO | 0.3 |
| g02 | 20 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 9.6 |
| g03 | 20 | rice Nairobi 160 | rice Nairobi 160 | yes | 7.1 |
| g04 | 20 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 2.2 |
| g05 | 20 | beans Kitale 220 | beans Kitale 220 | yes | 12.3 |
| g06 | 20 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 0.4 |
| g07 | 20 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 4.3 |
| g08 | 20 | beans Arusha 3500 | beans Arusha 23 | NO | 0.5 |
| g09 | 20 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 9.2 |
| g10 | 20 | maize Morogoro 74000 | maize Morogoro 84 | NO | 2.9 |
| g11 | 20 | maize Kakamega 3800 | maize Kakamega 3800 | yes | 3.3 |
| g12 | 20 | rice Mombasa 190 | rice Mombasa 190 | yes | 7.0 |
| g13 | 20 | beans Kisii 9500 | beans Kisii 309 | NO | 12.5 |
| g14 | 20 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 4.7 |
| g15 | 20 | maize Gulu 1500 | maize Gulu 1100 | NO | 2.4 |
| g16 | 20 | rice Dar es Salaam 2800 | rice Dar es Salaam 80 | NO | 3.1 |
| g17 | 20 | beans Dodoma 3000 | beans Dodoma 3000 | yes | 7.1 |
| g18 | 20 | maize Kampala 1800 | maize Mbeya 1800 | yes | 4.5 |
| g19 | 20 | beans Mwanza 250000 | beans Mwanza 23 | NO | 4.2 |
| g20 | 20 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 9.0 |
| g01 | 8 | maize Kisumu 5200 | maize Kisumu 30 | NO | 8.4 |
| g02 | 8 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 11.4 |
| g03 | 8 | rice Nairobi 160 | rice Nairobi 160 | yes | 6.9 |
| g04 | 8 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 10.0 |
| g05 | 8 | beans Kitale 220 | beans Kitale 220 | yes | 11.2 |
| g06 | 8 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 0.9 |
| g07 | 8 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 5.1 |
| g08 | 8 | beans Arusha 3500 | beans Arusha 23 | NO | 2.9 |
| g09 | 8 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 4.0 |
| g10 | 8 | maize Morogoro 74000 | maize Morogoro 34000 | NO | 10.0 |
| g11 | 8 | maize Kakamega 3800 | maize Kakamega 23 | NO | 10.0 |
| g12 | 8 | rice Mombasa 190 | rice Mombasa 190 | yes | 6.3 |
| g13 | 8 | beans Kisii 9500 | maize Mbeya 4 | NO | 1.3 |
| g14 | 8 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 5.1 |
| g15 | 8 | maize Gulu 1500 | maize Mbeya 1100 | NO | 1.3 |
| g16 | 8 | rice Dar es Salaam 2800 | rice Dar es Salaam 34 | NO | 2.8 |
| g17 | 8 | beans Dodoma 3000 | rice Mbeya 2 | NO | 8.6 |
| g18 | 8 | maize Kampala 1800 | maize Mbeya 32 | NO | 0.8 |
| g19 | 8 | beans Mwanza 250000 | beans Mwanza 2 | NO | 10.0 |
| g20 | 8 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 7.8 |

## Abstain tests (g21 coffee, g22 weather news; vocabulary does not contain the content)

| id | cond | free text | grammar-forced text | margin | free-vs-constrained loglik gap |
|---|---|---|---|---|---|
| g21 | 12 | mbia kahawa na kuu ni shiingi elfu mbili wa kilwa | mahindi mbeya ni kumi na nne | 1.1 | -27.6 |
| g21 | 20 | mbia kahawa na kuu ni shinningi elfu mbili wa kilwa | mahindi nairobi ni kumi | 0.8 | -16.9 |
| g21 | 8 | mbia kahawa na kuru nishiringi elfu mbili ripo wakini | mahindi mbeya ni kumi na mbili | 0.2 | -28.0 |
| g22 | 12 | habari za ndege huvua kubwa ni mbininisha kisumbu si kuwa njaana | kampala bei ya mchele ni mbili | 3.5 | -45.9 |
| g22 | 20 | habari za ndayo huvua kubwa ni mbininisha kisumbu si kuwa njaana | morogoro bei ya maharage ni kumi | 1.0 | -42.7 |
| g22 | 8 | habari za ndege huvua kubwa ni mtingisha kisumbu usiku wa njaana | kampala leo bei ya maharage ni kumi | 1.6 | -52.1 |
