from typing import List, Tuple
import fugashi
import random

tagger = fugashi.Tagger()


def get_reading(text: str) -> str:
    return ''.join(w.feature.kana or w.surface for w in tagger(text))


def count_mora(text: str) -> int:
    return len(get_reading(text))


def split_mora_units(text: str) -> List[str]:
    words = tagger(text)
    return [w.surface for w in words]


def is_poetic_phrase(tokens: List[Tuple[str, str, int, str]]) -> bool:
    if not tokens or len(tokens) < 2:
        return False  # 一語句は基本弾く（味が出ない）

    start_pos = tokens[0][3]
    end_pos = tokens[-1][3]

    # NG: 助詞・助動詞・記号で始まる or 終わる
    bad_boundary = {"助詞", "助動詞", "記号", "補助記号", "接続詞", "連体詞", "接頭辞"}
    if start_pos in bad_boundary or end_pos in bad_boundary:
        return False

    # 中に名詞・動詞・形容詞・副詞が含まれていれば OK
    core_pos = {"名詞", "動詞", "形容詞", "副詞", "感動詞", "形容動詞"}
    has_content = any(pos in core_pos for _, _, _, pos in tokens)
    if not has_content:
        return False

    return True

def score_senryu(first, second, third) -> float:
    score = 0.0

    # 品詞の連なり評価（流れが自然か）
    def is_smooth_transition(a, b) -> bool:
        _, _, _, pos_a = a[-1]
        _, _, _, pos_b = b[0]
        smooth_pairs = {
            ("名詞", "助詞"),
            ("助詞", "動詞"),
            ("動詞", "名詞"),
            ("形容詞", "名詞"),
        }
        return (pos_a, pos_b) in smooth_pairs

    if is_smooth_transition(first, second):
        score += 1.0
    if is_smooth_transition(second, third):
        score += 1.0

    # 情感のある品詞が多いほど加点（感動詞・形容詞・副詞など）
    emotive_pos = {"感動詞", "形容詞", "副詞", "形容動詞"}
    for phrase in [first, second, third]:
        score += sum(1 for _, _, _, pos in phrase if pos in emotive_pos) * 0.3

    # 句の長さが適切に分散してるほど加点（例：短・長・短）
    score += len(first) * 0.1 + len(second) * 0.1 + len(third) * 0.1

    return score

def extract_best_senryu(text: str, debug: bool = True) -> List[str]:
    words = [(w.surface, w.feature.kana or w.surface, len(w.feature.kana or w.surface), w.feature.pos1) for w in tagger(text)]
    candidates = {5: [], 7: []}

    for i in range(len(words)):
        total = 0
        for j in range(i, len(words)):
            total += words[j][2]
            if total in (5, 7):
                part = words[i:j+1]
                if is_poetic_phrase(part):
                    candidates[total].append(part)
                break
            elif total > 7:
                break

    if debug:
        print("🎲 候補句（5モーラ）:", [ ''.join(w for w, *_ in p) for p in candidates[5] ])
        print("🎲 候補句（7モーラ）:", [ ''.join(w for w, *_ in p) for p in candidates[7] ])

    combos_with_score = []
    for i in range(len(candidates[5])):
        for j in range(len(candidates[7])):
            for k in range(len(candidates[5])):
                if i == k:
                    continue
                first = candidates[5][i]
                second = candidates[7][j]
                third = candidates[5][k]

                score = score_senryu(first, second, third)
                senryu_text = [
                    ''.join(w for w, *_ in first),
                    ''.join(w for w, *_ in second),
                    ''.join(w for w, *_ in third),
                ]
                combos_with_score.append((score, senryu_text))

    if not combos_with_score:
        if debug:
            print("❌ 川柳を構成できませんでした")
        return []

    # スコア順に降順ソート
    combos_with_score.sort(reverse=True, key=lambda x: x[0])

    # 最もスコアの高いものを返す
    return combos_with_score[0][1]
