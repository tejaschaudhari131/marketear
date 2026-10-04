# GO/NO-GO gate report (simulated FM channel; one speaker, scripted sentences)

Pass criterion per sentence: crop AND exact price both correct. Gate: GO if either route reaches >=16 of 20 at 12 dB CNR.

| condition | free ASR + fuzzy parser | closed-grammar decoder | closed-grammar decoder with abstain (margin >= n/a) |
|---|---|---|---|
| 20 dB | 9/20 | 18/20 | n/a |
| 12 dB | 8/20 | 19/20 | n/a |
| 8 dB | 10/20 | 18/20 | n/a |

**GATE RESULT: GO** (12 dB: free route 8/20, closed-grammar route 19/20; threshold 16/20)


## Per-sentence detail (closed-grammar decoder)

| id | cond | truth | decoded | ok | margin |
|---|---|---|---|---|---|
| g01 | 12 | maize Kisumu 5200 | maize Kisumu 5200 | yes | 14.5 |
| g02 | 12 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 13.4 |
| g03 | 12 | rice Nairobi 160 | rice Nairobi 160 | yes | 4.6 |
| g04 | 12 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 10.0 |
| g05 | 12 | beans Kitale 220 | beans Kitale 220 | yes | 9.3 |
| g06 | 12 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 10.0 |
| g07 | 12 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 7.9 |
| g08 | 12 | beans Arusha 3500 | beans Arusha 3500 | yes | 9.7 |
| g09 | 12 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 5.6 |
| g10 | 12 | maize Morogoro 74000 | maize Morogoro 74000 | yes | 5.1 |
| g11 | 12 | maize Kakamega 3800 | maize Kakamega 3800 | yes | 4.4 |
| g12 | 12 | rice Mombasa 190 | rice Mombasa 190 | yes | 24.6 |
| g13 | 12 | beans Kisii 9500 | beans Kisii 9500 | yes | 2.1 |
| g14 | 12 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 3.0 |
| g15 | 12 | maize Gulu 1500 | maize Gulu 1500 | yes | 11.3 |
| g16 | 12 | rice Dar es Salaam 2800 | rice Dar es Salaam 2800 | yes | 6.1 |
| g17 | 12 | beans Dodoma 3000 | beans Dodoma 3000 | yes | 14.5 |
| g18 | 12 | maize Kampala 1800 | maize Kampala 1800 | yes | 5.7 |
| g19 | 12 | beans Mwanza 250000 | rice Mwanza 250000 | NO | 13.7 |
| g20 | 12 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 5.5 |
| g01 | 20 | maize Kisumu 5200 | maize Kisumu 5200 | yes | 14.7 |
| g02 | 20 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 13.6 |
| g03 | 20 | rice Nairobi 160 | rice Nairobi 160 | yes | 4.6 |
| g04 | 20 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 10.0 |
| g05 | 20 | beans Kitale 220 | beans Kitale 220 | yes | 8.6 |
| g06 | 20 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 10.0 |
| g07 | 20 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 3.8 |
| g08 | 20 | beans Arusha 3500 | beans Arusha 3500 | yes | 10.0 |
| g09 | 20 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 4.9 |
| g10 | 20 | maize Morogoro 74000 | maize Morogoro 74000 | yes | 5.2 |
| g11 | 20 | maize Kakamega 3800 | maize Kakamega 3800 | yes | 4.4 |
| g12 | 20 | rice Mombasa 190 | rice Mombasa 190 | yes | 24.5 |
| g13 | 20 | beans Kisii 9500 | maize Kisii 9500 | NO | 2.0 |
| g14 | 20 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 4.6 |
| g15 | 20 | maize Gulu 1500 | maize Gulu 1500 | yes | 9.7 |
| g16 | 20 | rice Dar es Salaam 2800 | rice Dar es Salaam 2800 | yes | 6.0 |
| g17 | 20 | beans Dodoma 3000 | beans Dodoma 3000 | yes | 14.4 |
| g18 | 20 | maize Kampala 1800 | maize Kampala 1800 | yes | 5.1 |
| g19 | 20 | beans Mwanza 250000 | rice Mwanza 250000 | NO | 12.9 |
| g20 | 20 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 5.6 |
| g01 | 8 | maize Kisumu 5200 | maize Kisumu 5200 | yes | 14.5 |
| g02 | 8 | beans Nakuru 12000 | beans Nakuru 12000 | yes | 11.4 |
| g03 | 8 | rice Nairobi 160 | rice Nairobi 160 | yes | 4.6 |
| g04 | 8 | maize Eldoret 4500 | maize Eldoret 4500 | yes | 10.0 |
| g05 | 8 | beans Kitale 220 | beans Kitale 220 | yes | 6.8 |
| g06 | 8 | maize Dodoma 1200 | maize Dodoma 1200 | yes | 10.0 |
| g07 | 8 | rice Mwanza 2900 | rice Mwanza 2900 | yes | 7.9 |
| g08 | 8 | beans Arusha 3500 | beans Arusha 3500 | yes | 14.1 |
| g09 | 8 | maize Mbeya 85000 | maize Mbeya 85000 | yes | 5.1 |
| g10 | 8 | maize Morogoro 74000 | maize Morogoro 74000 | yes | 5.5 |
| g11 | 8 | maize Kakamega 3800 | maize Kakamega 3800 | yes | 5.3 |
| g12 | 8 | rice Mombasa 190 | rice Mombasa 190 | yes | 10.5 |
| g13 | 8 | beans Kisii 9500 | maize Kisii 9500 | NO | 7.3 |
| g14 | 8 | maize Kisumu 5300 | maize Kisumu 5300 | yes | 4.1 |
| g15 | 8 | maize Gulu 1500 | maize Gulu 1500 | yes | 10.0 |
| g16 | 8 | rice Dar es Salaam 2800 | rice Dar es Salaam 2800 | yes | 6.4 |
| g17 | 8 | beans Dodoma 3000 | beans Dodoma 3000 | yes | 14.6 |
| g18 | 8 | maize Kampala 1800 | maize Kampala 1800 | yes | 5.7 |
| g19 | 8 | beans Mwanza 250000 | maize Mwanza 250000 | NO | 16.6 |
| g20 | 8 | maize Nakuru 6750 | maize Nakuru 6750 | yes | 5.7 |

## Abstain tests (g21 coffee, g22 weather news; vocabulary does not contain the content)

| id | cond | free text | grammar-forced text | margin | free-vs-constrained loglik gap |
|---|---|---|---|---|---|
| g21 | 12 | liyakahawa na kuwa ni shilingi elfu mbili kwa kino | dar es salaam bei ya mahindi ni shilingi elfu mbili kwa kilo | 6.3 | -34.9 |
| g21 | 20 | diya kahawa na kuwa ni shilingi elfu mbili kwa kilo | dar es salaam bei ya mahindi ni shilingi elfu mbili kwa kilo | 8.9 | -33.1 |
| g21 | 8 | di ya kahawa na kuwa ni shilingi elfu mbili kwa kilo | dar es salaam bei ya mahindi ni shilingi elfu mbili kwa kilo | 11.3 | -28.5 |
| g22 | 12 | habari za leo mvua kubwa imenyesha kisumu usiku wa jaha | kisumu bei ya maharage ni kumi | 0.8 | -51.9 |
| g22 | 20 | habari za leo mvua kubwa imenyesha kisumu usiku wa jaha | kisumu bei ya maharage ni kumi | 0.8 | -52.0 |
| g22 | 8 | kabari za leo mvua kubwa imenyesha kisumu usiku wa jaha | dar es salaam bei ya maharage ni kumi | 1.1 | -45.9 |
