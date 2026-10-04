# Video script — Market Ear v2 (target 3 min 40 s; limit 5:00, minimum 2:00)

Record the screen of the demo (`python ui/server.py`, browser at the printed address) plus a voice-over. Everything on screen that involves the radio channel is a simulation and the narration says so. Numbers in this script are measured values from `STATUS.md`; if a number is re-measured before recording, change the script to match.

**0:00-0:25 Problem statement (one sentence, as the brief requires), on a slide.**
"Because of this tool, the co-op clerk will text members the maize or bean price a Swahili radio station read out, next to the World Food Programme range for that market, within minutes of the broadcast, which members would otherwise miss or hear with nothing to compare it to; we know because radio is the most common news source for many Africans (Afrobarometer, 59 percent weekly, from the Hack-Nation brief), because WFP publishes monthly market prices for 226 Kenyan markets, and because we measured how well a small model recovers crop and price from simulated radio audio, and we show where it fails."
Visual: Noor on the slope, the middleman at harvest naming a price (title card, text only).

**0:25-1:05 AI capabilities and guardrails (slide with the pipeline).**
"A Swahili speech model, Whisper small fine-tuned on Swahili, listens. The key idea: it is not allowed to write free text. At every step it may only choose words from a closed list: three crops, sixteen markets, six units, and Swahili number words like 'elfu tano na mia mbili'. A free transcript of Swahili makes mistakes in prices; on real broadcast speech it got 13 of 17 multi-word numbers exactly right, and the closed-number decoder got 16 of 17. A simpler tool, an SMS service or a spreadsheet, cannot do this, because the broadcast itself is the data source and has to be listened to in Swahili. Guardrails: it abstains if another crop or price fits almost as well, if the audio does not fit the closed list, or if WFP has no recent data; and a person confirms."

**1:05-2:35 Tool demo, screen recording, end to end.**
1. (1:05) "This is the clerk's screen. Banner: nothing is sent from here." Choose the example "Kisumu maize 5,200" (synthetic speech). Turn the channel to SIMULATED FM 12 dB; point at the yellow label. Press Listen.
2. (1:30) Result: decoded text, extracted crop, market, price, unit. WFP box: "KES 3,900 to 5,600, median 5,200, 19 monthly values, December 2024 to July 2026, Kibuye market, Kisumu. Inside the range." Show the Swahili draft message and the English message; say the Swahili is a draft awaiting a native speaker.
3. (1:55) Choose "Kisumu maize 7,200": above the range. Say: "This is a comparison, not advice."
4. (2:05) Choose the coffee clip: NOT SURE - ask a person, with the reason. Choose the weather clip: same. Choose the Dar es Salaam rice clip: price read, "No reference", because WFP's Tanzanian per-kilo series ends in December 2022.
5. (2:20) Play Tejas's own recording through the same screen (use only if the gate recording is available; its result is whatever it is, shown honestly). Press Confirm: "Nothing was sent: this demo has no send function."

**2:35-3:05 The gap and where it sits in the user's day (slide), with tech stack.**
"The clerk opens it after the midday price bulletin on the local station, checks the proposed message, confirms, and members get an SMS or a short voice line before the buyer arrives. Stack: Python, Whisper small with a grammar-constrained beam search, a software FM channel simulator, WFP price files from HDX, a local web page; no internet needed after the model is on the laptop. Model size: see the table below."
Slide: model size table from `docs/EVALUATION.md` (fp32, fp16, int8 dynamic) with the measured accuracy change.

**3:05-3:30 Evidence and limits (slide: the evaluation table).**
"Everything radio here is simulated and the scripted speech is synthetic or one speaker. On synthetic bulletins through the simulated channel, from clean down to 5 dB, the closed-grammar decoder read crop and price in 36 of 36 clips, against 26 of 36 for a free transcript plus a parser. On the gate recording, the result is on the next slide. No real market bulletin audio exists in open data, so we have not tested on a real station. A study in Niger found mobile coverage alone did not raise producer prices, so we claim a faster, checkable reference, not higher pay."

**3:30-3:50 Your take (Tejas, in his own words; this is a draft he should adjust).**
"For me, localizing AI means the model has to be small enough to sit in the co-op office, speak the farmer's language, only say what it can back up with a public number, and say 'not sure' out loud. A confident wrong price is worse than no price. The next step is a native Swahili speaker checking every word, and a real radio station letting us test on its actual bulletins."

**Close (3:50):** card with repository link, the referral code WBGSmallAIGADS, and the words "Simulated channel. Synthetic and scripted speech. Human decides."
