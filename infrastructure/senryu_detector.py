from typing import List, Tuple
import fugashi
import random

tagger = fugashi.Tagger()

def is_poetic_phrase(tokens: List[Tuple[str, str, int, str]]) -> bool:
    if len(tokens) < 2:
        return False

    pos_list = [t[3] for t in tokens]
    bad_boundary = {"助詞", "助動詞", "記号", "補助記号", "接続詞", "連体詞", "接頭辞"}
    if pos_list[0] in bad_boundary or pos_list[-1] in bad_boundary:
        return False

    core_pos = {"名詞", "動詞", "形容詞", "副詞", "感動詞", "形容動詞"}
    return any(pos in core_pos for pos in pos_list)

def extract_random_senryu(text: str, debug: bool = True) -> List[str]:
    words = [
        (w.surface, w.feature.kana or w.surface, len(w.feature.kana or w.surface), w.feature.pos1)
        for w in tagger(text)
    ]

    def find_phrases(mora_target: int) -> List[List[Tuple[str, str, int, str]]]:
        results = []
        for i in range(len(words)):
            total = 0
            phrase = []
            for j in range(i, len(words)):
                surface, reading, mora, pos = words[j]
                total += mora
                if total > mora_target:
                    break
                phrase.append((surface, reading, mora, pos))
                if total == mora_target and is_poetic_phrase(phrase):
                    results.append(phrase)
                    break
        return results

    candidates_5 = find_phrases(5)
    candidates_7 = find_phrases(7)

    if debug:
        print("🎲 候補句（5モーラ）:", [''.join(w for w, *_ in p) for p in candidates_5])
        print("🎲 候補句（7モーラ）:", [''.join(w for w, *_ in p) for p in candidates_7])

    if len(candidates_5) < 2 or not candidates_7:
        return []

    def phrase_text(phrase: List[Tuple[str, str, int, str]]) -> str:
        return ''.join(w for w, *_ in phrase)

    used_texts = set()

    first = random.choice(candidates_5)
    used_texts.add(phrase_text(first))

    candidates_7_filtered = [p for p in candidates_7 if phrase_text(p) not in used_texts]
    if not candidates_7_filtered:
        return []
    second = random.choice(candidates_7_filtered)
    used_texts.add(phrase_text(second))

    candidates_5_filtered = [p for p in candidates_5 if phrase_text(p) not in used_texts]
    if not candidates_5_filtered:
        return []
    third = random.choice(candidates_5_filtered)

    return [
        phrase_text(first),
        phrase_text(second),
        phrase_text(third),
    ]
