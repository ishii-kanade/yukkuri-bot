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



def extract_random_senryu(text: str, debug: bool = True) -> List[str]:
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

    if len(candidates[5]) < 2 or not candidates[7]:
        if debug:
            print("❌ 十分な候補がありません")
        return []

    first, third = random.sample(candidates[5], 2)
    second = random.choice(candidates[7])

    return [
        ''.join(w for w, *_ in first),
        ''.join(w for w, *_ in second),
        ''.join(w for w, *_ in third),
    ]
