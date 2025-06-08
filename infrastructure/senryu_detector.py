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

def score_phrase(phrase: List[Tuple[str, str, int, str]]) -> float:
    pos_list = [t[3] for t in phrase]
    score = 0.0

    # 情報量のある品詞に加点
    core_pos = {"名詞", "動詞", "形容詞", "副詞", "形容動詞", "感動詞"}
    score += sum(1 for pos in pos_list if pos in core_pos) * 1.0

    # 助詞や補助記号ばかりなら減点
    filler_pos = {"助詞", "助動詞", "記号", "補助記号"}
    if all(pos in filler_pos for pos in pos_list):
        score -= 2.0

    return score

def score_senryu(first, second, third) -> float:
    score = score_phrase(first) + score_phrase(second) + score_phrase(third)

    def transition_score(a, b):
        _, _, _, pos_a = a[-1]
        _, _, _, pos_b = b[0]
        good_transitions = {
            ("名詞", "助詞"),
            ("助詞", "動詞"),
            ("形容詞", "名詞"),
            ("動詞", "名詞"),
        }
        return 1.0 if (pos_a, pos_b) in good_transitions else 0.0

    score += transition_score(first, second)
    score += transition_score(second, third)

    return score

def extract_sequential_senryu(text: str, debug: bool = True) -> List[str]:
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
        print("📋 候補句（5モーラ）:", [''.join(w for w, *_ in p) for p in candidates_5])
        print("📋 候補句（7モーラ）:", [''.join(w for w, *_ in p) for p in candidates_7])

    if len(candidates_5) < 2 or not candidates_7:
        return []

    def phrase_text(phrase: List[Tuple[str, str, int, str]]) -> str:
        return ''.join(w for w, *_ in phrase)

    used_texts = set()

    first = candidates_5[0]
    used_texts.add(phrase_text(first))

    second = next((p for p in candidates_7 if phrase_text(p) not in used_texts), None)
    if not second:
        return []
    used_texts.add(phrase_text(second))

    third = next((p for p in candidates_5 if phrase_text(p) not in used_texts), None)
    if not third:
        return []

    return [
        phrase_text(first),
        phrase_text(second),
        phrase_text(third),
    ]

def extract_best_sequential_senryu(text: str, debug: bool = True) -> List[str]:
    words = [
        (w.surface, w.feature.kana or w.surface, len(w.feature.kana or w.surface), w.feature.pos1)
        for w in tagger(text)
    ]

    def find_phrases(mora_target: int, start_idx: int) -> List[Tuple[int, List[Tuple[str, str, int, str]]]]:
        results = []
        for i in range(start_idx, len(words)):
            total = 0
            phrase = []
            for j in range(i, len(words)):
                surface, reading, mora, pos = words[j]
                total += mora
                if total > mora_target:
                    break
                phrase.append((surface, reading, mora, pos))
                if total == mora_target and is_poetic_phrase(phrase):
                    results.append((j + 1, phrase))
                    break
        return results

    best_score = float('-inf')
    best_combo = []

    for i, first in find_phrases(5, 0):
        for j, second in find_phrases(7, i):
            for k, third in find_phrases(5, j):
                score = score_senryu(first, second, third)
                if score > best_score:
                    best_score = score
                    best_combo = [first, second, third]

    if not best_combo:
        if debug:
            print("❌ 川柳構成に失敗しました")
        return []

    def phrase_text(phrase: List[Tuple[str, str, int, str]]) -> str:
        return ''.join(w for w, *_ in phrase)

    result = [phrase_text(p) for p in best_combo]

    if debug:
        print("🏆 スコア最高の川柳:")
        for line in result:
            print(line)
        print(f"🎯 Score: {best_score}")

    return result
