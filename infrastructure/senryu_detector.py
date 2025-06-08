from typing import List, Tuple
import fugashi
import re

tagger = fugashi.Tagger()

Token = Tuple[str, str, int, str]  # surface, reading, mora, pos


def is_poetic_phrase(tokens: List[Token]) -> bool:
    if len(tokens) < 2:
        return False
    pos_list = [t[3] for t in tokens]
    bad_boundary = {"助詞", "助動詞", "記号", "補助記号", "接続詞", "連体詞", "接頭辞"}
    core_pos = {"名詞", "動詞", "形容詞", "副詞", "感動詞", "形容動詞"}
    return not (pos_list[0] in bad_boundary or pos_list[-1] in bad_boundary) and any(pos in core_pos for pos in pos_list)


def score_phrase(phrase: List[Token]) -> float:
    pos_list = [t[3] for t in phrase]
    core_pos = {"名詞", "動詞", "形容詞", "副詞", "形容動詞", "感動詞"}
    filler_pos = {"助詞", "助動詞", "記号", "補助記号"}
    score = sum(1 for pos in pos_list if pos in core_pos)
    if all(pos in filler_pos for pos in pos_list):
        score -= 2.0
    return score


def transition_score(a: List[Token], b: List[Token]) -> float:
    _, _, _, pos_a = a[-1]
    _, _, _, pos_b = b[0]
    good_transitions = {("名詞", "助詞"), ("助詞", "動詞"), ("形容詞", "名詞"), ("動詞", "名詞")}
    return 1.0 if (pos_a, pos_b) in good_transitions else 0.0


def score_senryu(first: List[Token], second: List[Token], third: List[Token]) -> float:
    return (score_phrase(first) + score_phrase(second) + score_phrase(third)
            + transition_score(first, second) + transition_score(second, third))


def extract_best_sequential_senryu(text: str, debug: bool = True) -> List[str]:

    def is_japanese_token(token: Token) -> bool:
        surface, reading, _, pos = token

        # 弾きたい品詞
        banned_pos = {"記号", "補助記号", "空白"}

        if pos in banned_pos:
            return False
        if re.fullmatch(r'[a-zA-Z0-9]+', surface):
            return False
        if re.fullmatch(r'\s+', surface):
            return False
        return True


    words = [(w.surface, w.feature.kana or w.surface, len(w.feature.kana or w.surface), w.feature.pos1)
             for w in tagger(text)]

    words = [token for token in words if is_japanese_token(token)]

    def find_phrases(mora_target: int, start_idx: int) -> List[Tuple[int, List[Token]]]:
        results = []
        for i in range(start_idx, len(words)):
            total, phrase = 0, []
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

    candidates_5 = find_phrases(5, 0)
    best_score, best_combo, candidates_7_all = float('-inf'), [], []

    for i, first in candidates_5:
        candidates_7 = find_phrases(7, i)
        candidates_7_all.extend(candidates_7)
        for j, second in candidates_7:
            for k, third in find_phrases(5, j):
                score = score_senryu(first, second, third)
                if score > best_score:
                    best_score, best_combo = score, [first, second, third]

    if not best_combo:
        if debug:
            print("❌ 川柳構成に失敗しました")
        return []

    def phrase_text(phrase: List[Token]) -> str:
        return ''.join(w for w, *_ in phrase)

    def print_phrase_detail(title: str, phrase_list: List[List[Token]]):
        print(f"\n📋 {title}（{len(phrase_list)}件）:")
        for phrase in phrase_list:
            text = phrase_text(phrase)
            mora = sum(m for _, _, m, _ in phrase)
            print(f"- {text}（{mora}モーラ）")
            for surface, reading, mora, pos in phrase:
                print(f"    ・{surface}（{reading}）: {mora}モーラ, 品詞: {pos}")

    if debug:
        print("🏆 スコア最高の川柳:")
        for i, phrase in enumerate(best_combo):
            line = phrase_text(phrase)
            mora = sum(m for _, _, m, _ in phrase)
            print(f"\n句{i+1}: {line}（{mora}モーラ）")
            for surface, reading, mora, pos in phrase:
                print(f"  - {surface}（{reading}）: {mora}モーラ, 品詞: {pos}")
        print(f"\n🎯 Score: {best_score}")
        print_phrase_detail("5モーラ候補句", [p for _, p in candidates_5])
        print_phrase_detail("7モーラ候補句", [p for _, p in candidates_7_all])

    return [phrase_text(p) for p in best_combo]
