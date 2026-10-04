import json
rows = json.load(open("recording/script.json"))
L = []
L.append("# Market Ear v2 — recording script for the go/no-go gate (22 sentences, about 3 minutes)\n")
L.append("**Status of the Swahili text: NOT checked by a native speaker (native-speaker check flag = OPEN).** Every sentence was written by the build agent from the number grammar in `src/swnum.py`; the spelling and number words follow standard Swahili, but nobody fluent has confirmed them. If anyone at the hackathon speaks Swahili, ask them to glance at this page (2 minutes) or, better, to record the sentences instead of you.\n")
L.append("## What you do (about 10 minutes)\n")
L.append("1. Find a quiet room. Close the door, switch off fans and music. Hold the phone about a hand-span (15 cm) from your mouth.\n"
 "2. Open the voice recorder app (iPhone: Voice Memos; Android: Recorder or Voice Recorder). Record **one single file** for all 22 sentences.\n"
 "3. Read the sentences below **in order, one after another**, like a radio announcer: calm, clear, not rushed. **Leave a silent gap of about 3 seconds between sentences** (count 'one-two-three' in your head). Do not say the sentence number out loud.\n"
 "4. If you stumble: stay silent for 5 seconds, then read that same sentence again from the start. Keep going. Do not stop the recording.\n"
 "5. Say the numbers as words exactly as written (e.g. 'elfu tano na mia mbili'). Swahili is spelled the way it sounds: say every letter; stress the second-to-last syllable of a word; 'mb', 'nd', 'ng' at the start of a word are said as one quick sound.\n"
 "6. Stop the recording. Save it. Name it `marketear_gate.m4a` (or leave the default name).\n")
L.append("## How to send the file\n")
L.append("Any one of these works; tell the agent which one you used:\n"
 "- **Easiest:** drop the audio file straight into the chat as an attachment (it lands in `/workspace/uploads`).\n"
 "- Or save it on your MSI laptop (for example in Downloads) and tell the agent the file name; the agent copies it from there.\n"
 "- iPhone: Voice Memos → share → AirDrop/email to yourself → save on the laptop. Android: Recorder → share → Drive/email/USB.\n"
 "Formats m4a, mp3, wav, ogg, and amr all work. Do not edit, trim, or filter it.\n")
L.append("## Pronunciation hints (a non-native reader is fine; this is also a useful accent test and the report will say so)\n"
 "- a = 'ah', e = 'eh', i = 'ee', o = 'oh', u = 'oo'. Every vowel is said separately.\n"
 "- 'mahindi' = ma-HEEN-dee; 'maharage' = ma-ha-RA-geh; 'mchele' = m-CHEH-leh; 'shilingi' = shee-LEEN-gee; 'elfu' = EL-foo; 'mia' = MEE-ah; 'laki' = LAH-kee; 'gunia' = goo-NEE-ah; 'kilo' = KEE-lo.\n"
 "- 'th' (as in 'thelathini', 'themanini') is a soft 'th' like in English 'think'.\n")
L.append("## The sentences — read these in order\n")
L.append("| # | Read this aloud | What the system should hear (answer key, hidden from the recognizer) |\n|---|---|---|")
for r in rows:
    if r["kind"] == "gate":
        t = r["truth"]; a = f'{t["crop"]}, {t["place"]}, {t["price"]:,}, unit {t["unit"]}'
    else:
        a = "ABSTAIN TEST — " + r["why"]
    L.append(f'| {r["n"]} | {r["text"]}. | {a} |')
L.append("\nSentences 1-20 count for the go/no-go gate. Sentences 21 and 22 are on purpose outside the system's vocabulary: they test that it says 'not sure, ask a person' instead of guessing. Read them in the same calm voice.\n")
L.append("## What happens to your recording\n"
 "It stays on the build box. The agent cuts it into the 22 sentences at the silences, pushes each one through a **simulated** FM radio channel at three signal strengths (20, 12 and 8 dB carrier-to-noise), and checks whether the crop and the exact price come back right. Gate rule: GO if at least 16 of the 20 sentences give the right crop AND the exact price at 12 dB. The recording is your voice, read from a script, in a quiet room: it is a controlled test, not proof that the system works on a real radio station. The report will say so.\n")
open("recording/RECORDING_SCRIPT.md", "w").write("\n".join(L))
open("recording/sentences.txt", "w").write("\n".join(f'{r["n"]}. {r["text"]}.' for r in rows) + "\n")
