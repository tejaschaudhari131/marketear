import sys, json
sys.path.insert(0, "src")
from grammar import parse_sentence
GATE = [
 "Bei ya mahindi Kisumu leo ni shilingi elfu tano na mia mbili kwa gunia",
 "Bei ya maharage Nakuru ni shilingi elfu kumi na mbili kwa gunia",
 "Bei ya mchele Nairobi ni shilingi mia moja na sitini kwa kilo",
 "Mahindi Eldoret ni shilingi elfu nne na mia tano kwa gunia la kilo tisini",
 "Bei ya maharage Kitale leo ni shilingi mia mbili na ishirini kwa kilo",
 "Bei ya mahindi Dodoma ni shilingi elfu moja na mia mbili kwa kilo",
 "Bei ya mchele Mwanza ni shilingi elfu mbili na mia tisa kwa kilo",
 "Bei ya maharage Arusha ni shilingi elfu tatu na mia tano kwa kilo",
 "Mbeya leo bei ya mahindi ni shilingi elfu themanini na tano kwa gunia la kilo mia moja",
 "Bei ya mahindi Morogoro ni shilingi elfu sabini na nne kwa gunia la kilo mia moja",
 "Bei ya mahindi Kakamega ni shilingi elfu tatu na mia nane kwa gunia",
 "Bei ya mchele Mombasa ni shilingi mia moja na tisini kwa kilo",
 "Bei ya maharage Kisii ni shilingi elfu tisa na mia tano kwa gunia",
 "Kisumu bei ya mahindi ni shilingi elfu tano na mia tatu kwa gunia",
 "Bei ya mahindi Gulu ni shilingi elfu moja na mia tano kwa kilo",
 "Bei ya mchele Dar es Salaam ni shilingi elfu mbili na mia nane kwa kilo",
 "Bei ya maharage Dodoma ni shilingi elfu tatu kwa kilo",
 "Bei ya mahindi Kampala ni shilingi elfu moja na mia nane kwa kilo",
 "Bei ya maharage Mwanza ni shilingi laki mbili na elfu hamsini kwa gunia la kilo mia moja",
 "Bei ya mahindi Nakuru ni shilingi elfu sita na mia saba na hamsini kwa gunia",
]
EXTRA = [  # NOT counted in the gate: they test the abstain behaviour
 ("Bei ya kahawa Nakuru ni shilingi elfu mbili kwa kilo", "coffee is outside the closed vocabulary -> must abstain"),
 ("Habari za leo, mvua kubwa imenyesha Kisumu usiku wa jana", "weather news, no price -> must abstain"),
]
rows = []
for i, t in enumerate(GATE, 1):
    f = parse_sentence(t.lower().split()); assert all(f.values()), (t, f)
    rows.append({"n": i, "kind": "gate", "text": t, "truth": f})
for j, (t, why) in enumerate(EXTRA, 21):
    rows.append({"n": j, "kind": "abstain_test", "text": t, "truth": None, "why": why})
json.dump(rows, open("recording/script.json", "w"), indent=1, ensure_ascii=False)
print(len(rows), "sentences;", sum(r["kind"]=="gate" for r in rows), "gate")
