from typing import List, Tuple
import fugashi
import random

tagger = fugashi.Tagger()

def extract_random_senryu(text: str, debug: bool = True) -> List[str]:
    words = [(w.surface, w.feature.kana or w.surface, len(w.feature.kana or w.surface)) for w in tagger(text)]

    def find_phrases(mora_target: int) -> List[List[Tuple[str, str, int]]]:
        results = []
        for i in range(len(words)):
            total = 0
            phrase = []
            for j in range(i, len(words)):
                surface, reading, mora = words[j]
                total += mora
                if total > mora_target:
                    break
                phrase.append((surface, reading, mora))
                if total == mora_target:
                    results.append(phrase)
                    break
        return results

    candidates_5 = find_phrases(5)
    candidates_7 = find_phrases(7)

    if debug:
        print("🎲 候補句（5モーラ）:", [''.join(w for w, *_ in p) for p in candidates_5])
        print("🎲 候補句（7モーラ）:", [''.join(w for w, *_ in p) for p in candidates_7])

    if not candidates_5 or not candidates_7:
        return []

    # 完全ランダムで組む（同じ句が1句目と3句目になってもOKなら以下でよし）
    first = random.choice(candidates_5)
    second = random.choice(candidates_7)
    third = random.choice(candidates_5)

    return [
        ''.join(w for w, *_ in first),
        ''.join(w for w, *_ in second),
        ''.join(w for w, *_ in third),
    ]
