"""Free-ASR baseline: take the unconstrained transcript, snap each word to the closed vocabulary if close enough (difflib ratio), then parse.
This is the 'ASR + fuzzy parser' route that the closed-grammar decoder is compared against."""
import difflib
from grammar import CROPS, PLACES, FUNCTION_WORDS, UNITS, parse_sentence
from swnum import NUMBER_WORDS, parse as parse_num
VOCAB = sorted(set(list(CROPS) + [w for p in PLACES for w in p.split()] + FUNCTION_WORDS + list(NUMBER_WORDS) + [w for u in UNITS for w in u.split()]))
def snap(w, cut=0.78):
    if w in VOCAB: return w
    m = difflib.get_close_matches(w, VOCAB, n=1, cutoff=cut)
    return m[0] if m else w
def free_parse(text):
    ws = [snap(w) for w in text.split()]
    f = parse_sentence(ws)
    # lenient price: longest run of number words that parses
    best = None; i = 0
    while i < len(ws):
        if ws[i] in NUMBER_WORDS and ws[i] != "na":
            j = i
            while j < len(ws) and ws[j] in NUMBER_WORDS: j += 1
            run = ws[i:j]
            while run and run[-1] == "na": run = run[:-1]
            for k in range(len(run), 0, -1):
                v = parse_num(run[:k])
                if v is not None:
                    if best is None or k > best[0]: best = (k, v)
                    break
            i = j
        else: i += 1
    f["price"] = best[1] if best else None
    return f
