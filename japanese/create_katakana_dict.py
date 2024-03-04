import collections

from pathlib import Path

path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\japanese_mfa.dict")

new_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\japanese_katakana_mfa.dict")

katakana_chart = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
hiragana_chart = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"
hir2kat = str.maketrans(hiragana_chart, katakana_chart)
kat2hir =str.maketrans(katakana_chart, hiragana_chart)

mapping = collections.defaultdict(set)

extra_characters = 'ー・'

with open(path, 'r', encoding= 'utf8') as inf:
    for line in inf:
        line = line.strip()
        if not line:
            continue
        word, pron = line.split(maxsplit=1)
        if any(x not in katakana_chart+hiragana_chart + extra_characters for x in word):
            continue
        all_katakana = all(x in katakana_chart + extra_characters for x in word)
        all_hiragana = all(x in hiragana_chart + extra_characters for x in word)
        if not all_katakana:
            mapping[word.translate(hir2kat)].add(pron)
        mapping[word].add(pron)

skip = set()

for word, prons in sorted(mapping.items()):
    if '・' in word:
        norm_form = word.replace('・', '')
        if norm_form not in mapping:
            skip.add(word)
            continue
        mapping[word] = mapping[norm_form]

for word, prons in sorted(mapping.items()):
    if len(prons) > 1:

        print(word, prons)

print(len(mapping))

with open(new_path, 'w', encoding='utf8') as f:
    for word, prons in sorted(mapping.items()):
        if word in skip:
            continue
        for p in sorted(prons):
            f.write(f"{word}\t{p}\n")

print(skip)