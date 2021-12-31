# coding=utf8
import os
import re
from collections import Counter

import jamo

source_dir = r'D:\Data\speech\dictionaries\wikipron\raw'
output_dir = r'D:\Data\speech\dictionaries\wikipron\cleaned'
os.makedirs(output_dir, exist_ok=True)

lang_codes = ['bulgarian', 'croatian', 'czech', 'french', 'german', 'mandarin_hani', 'polish', 'portuguese_brazil',
              'portuguese_portugal', 'russian', 'spanish_castilian', 'spanish_latin_america', 'swedish',
              'tamil', 'thai', 'turkish', 'ukrainian',
              'korean_hangul', 'hausa', 'japanese', 'vietnamese_hanoi', 'vietnamese_hue', 'vietnamese_hochiminhcity']
lang_codes = ['english_us', 'english_uk']
# lang_codes = ['hausa']

bad_graphemes = {
    'english_us': {'%', '/', '@', '²', 'à', 'á', 'â', 'ä', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'í', 'î', 'ï', 'ñ', 'ó', 'ô',
                   'õ', 'ö', 'ø', 'ù', 'ú', 'ü', 'ā', 'ą', 'č', 'ē', 'ę', 'ğ', 'ı', 'ł', 'ń', 'ō', 'ő', 'œ', 'ř', 'ū',
                   'ș', 'ț', 'ʼ', 'ṭ', '₂'},
    'english_uk': {'%', '/', '@', '²', 'à', 'á', 'â', 'ä', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'í', 'î', 'ï', 'ñ', 'ó', 'ô',
                   'õ', 'ö', 'ø', 'ù', 'ú', 'ü', 'ā', 'ą', 'č', 'ē', 'ę', 'ğ', 'ı', 'ł', 'ń', 'ō', 'ő', 'œ', 'ř', 'ū',
                   'ș', 'ț', 'ʼ', 'ṭ', '₂', 'ã', 'å', 'û', 'ī', 'ž', '.'},
    'polish': {'+', '.', 'ü', 'ö', 'ø', 'ƶ', 'ñ', "ç", 'à', 'á', 'è', 'é', 'í'},
    'french': {'.', '/', 'º', 'å', 'æ', 'ÿ', 'ș'},
    'german': {"'", '.', '@', 'à', 'á', 'ç', 'è', 'é', 'ê', 'ó', 'ø', 'œ', 'í', 'ë'},
    'portuguese_brazil': {"'", '.', 'ü', 'è'},
    'portuguese_portugal': {"'", '.', 'ü', 'è'},
    'russian': {"'", '.', '/', 'ѳ'},
    'spanish_castilian': {"'", '.', 'ö', 'ü', 'ꝇ', 'î', 'ç'},
    'spanish_latin_america': {"'", '.', 'ö', 'ü', 'ꝇ', 'î', 'ç'},
    'thai': {'…', "'", '.', '/'},
    'turkish': {"̇", "'"},
    'tamil': {'ࢳ', 'ࢳ', 'ࢴ', 'ࢴ', 'ஃ'},
    'vietnamese_hanoi': {"'", '.', ',', },
    'vietnamese_hue': {"'", '.', ',', },
    'vietnamese_hochiminhcity': {"'", '.', ',', },
}

variation_mapping = {
    # '̥': '',
}


def read_source(lang):
    path = os.path.join(source_dir, '{}.tsv'.format(lang))
    graphemes = set()
    phones = set()
    dictionary = []
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if lang == 'russian':
                if ' ⁽ʲ ⁾' in line:
                    line_one = line.replace(' ⁽ʲ ⁾', 'ʲ')
                    line_two = line.replace(' ⁽ʲ ⁾', '')
                    line_one = line_one.split()
                    line_two = line_two.split()
                    word = line_one[0]
                    pronunciation_one = line_one[1:]
                    pronunciation_two = line_two[1:]
                    if lang in bad_graphemes:
                        if any(x in bad_graphemes[lang] for x in word):
                            print(word)
                            continue
                    graphemes.update(word)
                    phones.update(pronunciation_one)
                    phones.update(pronunciation_two)
                    dictionary.append((word, pronunciation_one))
                    dictionary.append((word, pronunciation_two))
                    continue
            elif lang == 'thai':
                if not re.search('[˥˩˦˧˨]', line):
                    continue
            elif lang == 'japanese_hiragana':
                if any(x in line for x in variation_mapping):
                    for k, v in variation_mapping.items():
                        if k not in line:
                            continue
                        line_one = line.replace(k, v)
                        line_two = line
                        line_one = line_one.split()
                        line_two = line_two.split()
                        word = line_one[0]
                        pronunciation_one = line_one[1:]
                        pronunciation_two = line_two[1:]
                        if lang in bad_graphemes:
                            if any(x in bad_graphemes[lang] for x in word):
                                print(word)
                                continue
                        graphemes.update(word)
                        phones.update(pronunciation_one)
                        phones.update(pronunciation_two)
                        dictionary.append((word, pronunciation_one))
                        dictionary.append((word, pronunciation_two))
                        break
                    continue
            elif lang == 'mandarin_hani':
                if '² ¹ ⁴ ⁻ ² ¹ ⁽ ⁴ ⁾' in line:
                    line = line.replace('² ¹ ⁴ ⁻ ² ¹ ⁽ ⁴ ⁾', '² ¹ ⁴')
                if '² ¹ ⁴ ⁻ ² ¹ ¹' in line:
                    line = line.replace('² ¹ ⁴ ⁻ ² ¹ ¹', '² ¹ ⁴')
                if '² ¹ ⁴ ⁻ ³ ⁵' in line:
                    line = line.replace('² ¹ ⁴ ⁻ ³ ⁵', '² ¹ ⁴')
                if '⁵ ¹ ⁻ ⁵ ³' in line:
                    line = line.replace('⁵ ¹ ⁻ ⁵ ³', '⁵ ¹')
                if '⁵ ⁵ ⁻ ⁵ ¹' in line:
                    line = line.replace('⁵ ⁵ ⁻ ⁵ ¹', '⁵ ⁵')
                skip_characters = ['² ⁴', 'ɚ', 'm̩', 'nʲ', 'v', '¹ ³', '¹ ¹', '⁴ ⁴', '² ⁴', '⁻', '⁽', '² ¹ ¹', '² ¹ ³', '⁵ ⁵ ³']
                if any(x in line for x in skip_characters):
                    continue
                if '⁻' in line:
                    line_one = re.sub(r' ⁻ [ ⁰¹²³⁴⁵]+', ' ', line)
                    line_one = line_one.split()
                    word = line_one[0]
                    if len(word) > 1:
                        continue
                    pronunciation_one = line_one[1:]
                    if lang in bad_graphemes:
                        if any(x in bad_graphemes[lang] for x in word):
                            print(word)
                            continue
                    graphemes.update(word)
                    phones.update(pronunciation_one)
                    dictionary.append((word, pronunciation_one))
                    continue
            if "\t" in line:
                line = line.split("\t")
                word = line[0]
                pronunciation = line[1].split()
            else:
                line = line.split()
                word = line[0]
                pronunciation = line[1:]
            if lang in bad_graphemes:
                if any(x in bad_graphemes[lang] for x in word):
                    print(word)
                    continue
            graphemes.update(word)
            phones.update(pronunciation)
            dictionary.append((word, pronunciation))
    return dictionary, graphemes, phones


bad_phones = {'english_uk': {'ɪː','aː', 'eː', 'a', 'o', 'oː', 'eː', 'e'},
              'english_us': {'ɒ', 'aː', 'a', 'o', 'oː', 'eː', 'e', 'ɪː', 'ɛː'}}

vowels = {
    'english_us': {'aɪ', 'aʊ', 'eɪ', 'i', 'iː', 'oɪ', 'oʊ', 'u', 'uː', 'æ',  'ɑ', 'ɑː', 'ɔ', 'ɔɪ', 'ɔː', 'ə', 'ɚ', 'ɛ', 'ɝ', 'ɝː', 'ɪ',  'ʊ', 'ʌ',},
    'english_uk': {'aɪ', 'aʊ', 'eɪ', 'i', 'iː', 'oɪ', 'oʊ', 'u', 'uː', 'æ',  'ɑ', 'ɑː', 'ɔ', 'ɔɪ', 'ɔː', 'ə', 'ɚ', 'ɛ', 'ɝ', 'ɝː', 'ɪ',  'ʊ', 'ʌ', 'aɪ', 'aʊ', 'eɪ', 'i', 'iː', 'oɪ', 'oʊ', 'u', 'uː', 'æ', 'ɑ', 'ɑː', 'ɒ', 'ɔ', 'ɔɪ', 'ɔː','ɛ', 'ɛː', 'ɜ', 'ɜː', 'ʊ', 'ʌ', },
    'vietnamese_hanoi': {'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'},
    'vietnamese_hue': {'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'},
    'vietnamese_hochiminhcity': {'a', 'aː', 'e', 'i', 'o', 'u', 'ɔ', 'ə', 'əː', 'ɛ', 'ɨ', 'ʊ', 'ɪ'},
    'mandarin_hani': {'a', 'e', 'o', 'i', 'u', 'y', 'ə', 'ɚ', 'ɤ̃', 'ʊ̃'},
    'thai': {'a', 'aj', 'aw', 'aː', 'aːj', 'aːw', 'e', 'ew', 'eː', 'eːw', 'i', 'iː', 'o', 'oː', 'oːj', 'u', 'uj',
                  'uə', 'uː', 'uːj', 'uːə', 'à', 'áː', 'ì', 'ǎː', 'ɔ', 'ɔj', 'ɔː', 'ɔːj', 'ɔ̌', 'ɛ', 'ɛw', 'ɛː', 'ɛːw',
                  'ɤ', 'ɤj', 'ɤː', 'ɤːj', 'ɯ', 'ɯː'},
    'swedish': {'a', 'aʊ', 'aː', 'e', 'eː', 'i', 'iː', 'o', 'oː', 'u', 'uː', 'y', 'yʷ', 'yː', 'æ', 'æː', 'êː', 'ø',
                  'øː', 'ø̀ː', 'œ', 'œː', 'œ̞', 'œ̞ː', 'ɑ', 'ɑː', 'ɒː', 'ɒ̀ː', 'ɔ', 'ə', 'ɚ', 'ɛ', 'ɛɵ', 'ɛː', 'ɛ̂',
                  'ɛ̄', 'ɜ', 'ɝ', 'ɪ', 'ɵ', 'ɵː', 'ɵ̄', 'ɶ', 'ɶː', 'ʉ', 'ʉː', 'ʉ̂ː', 'ʉ̟ː', 'ʊ', 'ʊː', 'ʏ', 'ỳː', 'ỵː'},
          }

def add_variation(word, phones, lang):
    variations = [(word, phones)]
    if lang in bad_phones:
        if any(x in bad_phones[lang] for x in phones):
            return []
    if lang == 'english_uk':
        if phones[:2] == ['t', 's']:
            return []
        prons = []
        for i, p in enumerate(phones):
            if p == 't' and 1 < i < len(phones) - 1 and phones[i-1] in vowels[lang] and phones[i + 1] in {'n̩', 'm̩', 'l̩', 'ɚ', 'ə', 'ɫ̩'}:
                prons.append([x if j != i else 'ʔ' for j, x in enumerate(phones)])
        if len(phones) > 1 and phones[-1] == 't' and phones[-2] in vowels[lang]:
            prons.append(phones[:-1] + ['ʔ'])
        for new_pron in prons:
            if new_pron == phones:
                continue
            variations.append((word, new_pron))
    elif lang == 'english_us':
        if phones[:2] == ['t', 's']:
            return []
        if word.endswith('r') and phones[-1] not in {'ɚ', 'ɹ', 'ɝ', 'ɝː'}:
            return []
        prons = []
        for i, p in enumerate(phones):
            if p == 'ə' and 1 < i < len(phones) - 2 and phones[i+1] in {'l', 'ɹ'} and phones[i+2] == 'ə': # Variable schwa deletion
                prons.append([x for j, x in enumerate(phones) if j != i])

        if len(phones) > 1 and phones[-1] == 't' and phones[-2] in vowels[lang]:
            prons.append(phones[:-1] + ['ʔ'])
        for new_pron in prons:
            if new_pron == phones:
                continue
            variations.append((word, new_pron))
    return variations


def save_dictionary(dictionary, lang):
    deduplication = set()
    final_phones = Counter()
    if lang == 'korean_hangul':
        from jamo import h2j
        path = os.path.join(output_dir, 'korean_jamo.txt'.format(lang))
        with open(path, 'w', encoding='utf8') as f:
            for w, p in dictionary:
                final_phones.update(p)
                p = ' '.join(p)
                if (w, p) in deduplication:
                    continue
                f.write('{}\t{}\n'.format(h2j(w), p))

    path = os.path.join(output_dir, '{}.txt'.format(lang))
    with open(path, 'w', encoding='utf8') as f:
        for w, p in sorted(dictionary):
            for w, p in add_variation(w, p, lang):
                final_phones.update(p)
                p = ' '.join(p)
                if (w, p) in deduplication:
                    continue
                f.write('{}\t{}\n'.format(w, p))
                deduplication.add((w, p))
    print("Final phones:", sorted(final_phones))
    print("Final phone counts:", sorted(final_phones.items(), key=lambda x: -x[1]))


lang_mapping = {
    'bulgarian': {
        'd̪': 'd',
        't̪': 't',
        'ɐ': 'a',
        'ə': 'ɤ',
        'o̝': 'ɔ',
        'lʲ': 'ɫ',
        'ɱ': 'mʲ',
        'ɾ': 'r',
    },
    'croatian': {
        'v': 'ʋ',
        'ô': 'o˦˨',
        'ôː': 'oː˦˨',
        'ûː': 'uː˦˨',
        'û': 'u˦˨',
        'î': 'i˦˨',
        'îː': 'iː˦˨',
        'êː': 'eː˦˨',
        'ê': 'e˦˨',
        'âː': 'aː˦˨',
        'â': 'a˦˨',
        'r̂': 'r̩˦˨',
        'r̂ː': 'r̩ː˦˨',
        'řː': 'r̩ː˨˦',
        'ř': 'r̩˨˦',
        'ěː': 'eː˨˦',
        'ě': 'e˨˦',
        'ǎ': 'a˨˦',
        'ǎː': 'aː˨˦',
        'ǐː': 'iː˨˦',
        'ǐ': 'i˨˦',
        'ǒ': 'o˨˦',
        'ǒː': 'oː˨˦',
        'ǔː': 'uː˨˦',
        'ǔ': 'u˨˦',
    },
    'french': {
        'r': 'ʁ'
    },
    'vietnamese_hanoi': {
        'k̟̚': 'k̚',
        'ŋ̟': 'ŋ',
        'ï': 'ɨ',
    },
    'german': {
        'b̥': 'p',
        'pʰ': 'p',
        'kʰ': 'k',
        'd̥': 't',
        'tʰ': 't',
        'ɡ̊': 'k',
        'r': 'ʁ',
        'ŋ̍': 'n̩',
        'ɱ̩': 'n̩',
        'ŋ̩': 'n̩',
        'ʀ': 'ʁ',
        'χ': 'x',
        'ʋ': 'v',
        'ɘ': 'ə',
    },
    'mandarin_hani': {
        'b̥': 'p',
        'd̥': 't',
        'g̊': 'k',
        'ɡ̊': 'k',
        'ɖʐ̥': 'ʈʂ',
        'dz̥': 'ts',
        'dʑ̥': 'tɕ',
        'ä': 'a',
        'æ̃': 'a',
        'ɤ': 'o',
        'ɤ̃': 'o',
        'ʊ̃': 'o',
        'ɪ': 'i',
        'ɻʷ': 'ɻ',
        'ʊ': 'u',
        'ɛ': 'e',
        'ɑ': 'a',
        'ɑ̃': 'a',
        'ɔ': 'o',
        'ɔː': 'o',
        '⁵⁵': '˥',
        '⁵¹': '˥˩',
        '³⁵': '˧˥',
        '²¹⁴': '˨˩˦',
    },
    'polish': {
        's̪': 's',
        'r̥ː': 'r',
        'r̥': 'r',
        'ɫ': 'l',
        'w̃': 'n',
    },
    'portuguese_brazil': {
        'õ': 'õ',  # Fix glyphs to use diacritics
        'ẽ': 'ẽ',
        'ũ': "ũ",
        'ĩ': "ĩ",
        'ã': 'ɐ̃',
        'ɫ': 'l',
        'ʁ': 'x',
        'ɹ': 'x',
        'ɻ': 'x',
        'χ': 'x',
        'ɦ': 'x',
        'h': 'x',
        'r': 'x',
        'ɪ': 'i',
        'ʊ': 'u',
    },
    'portuguese_portugal': {
        'õ': 'õ',  # Fix glyphs to use diacritics
        'ẽ': 'ẽ',
        'ũ': "ũ",
        'ĩ': "ĩ",
        'ã': 'ɐ̃',
        'ɫ': 'l',
        'r': 'ʁ',
    },
    'swedish': {
        'ɛ̄': 'ɛ̂',
        'ɵ̄': 'ɵ̂',
        'ʁ': 'r',
        'ɾ': 'r',
        'ɹ': 'r',
        'v': 'ʋ',
        'ˇl': 'l',
        'yʷ': 'y',
        'œ̞ː': 'œː',
        'œ̞': 'œ',
        'ç': 'ɕ',
        'bː': 'b',  # removing length in consonants
        'ɖː': 'ɖ',
        'ɖˑ': 'ɖ',
        'dː': 'd',
        'jː': 'j',
        'kː': 'k',
        'lː': 'l',
        'mː': 'm',
        'nː': 'n',
        'fː': 'f',
        'pː': 'p',
        'rː': 'r',
        'sː': 's',
        'tˑ': 't',
        'tː': 't',
        'ŋː': 'ŋ',
        'ɕː': 'ɕ',
        'ɡː': 'ɡ',
        'ʈː': 'ʈ',
        'ʂː': 'ʈ',
        'ỵː': 'yː',
        'ʉ̟̂': 'ʉ̂',
        'ʉ̟ː': 'ʉː',
        'ʉ̂': 'ʉ̂ː',
        'ɒː': 'ɑː',
        'ɑ': 'ɑː',
        'e': 'eː',
        'o': 'oː',
        'u': 'uː',
        'i': 'iː',
        'y': 'yː',
        'ɒ̀ː': 'ɑ̀ː',
        'ʊː': 'ʊ',
        'ʉ': 'ʉː',
        'ɶː': 'øː',
    },
    'tamil': {
        'l̪': 'l',
        'l̪ː': 'lː',
        'r̥': 'r',
        'ɾ̪': 'ɾ',
        'h': 'ɦ',
        'tʃ': 'tɕ',
        'ɕ': 'tɕ',
        'tʃː': 'tɕː',

    },
    'thai': {
        'cʰ': 'tɕʰ',
        'c': 'tɕ',
        'ɔ̌': 'ɔ˩˩˦',
        'ǎː': 'aː˩˩˦',
        'áː': 'aː˦˥',
        'à': 'a˨˩',
        'ì': 'i˨˩',
    },
    'ukrainian': {
        'ɫ': 'l',
        'ɫː': 'lː',
    },
    'japanese': {
        'o̞': 'o',
        'õ̞': 'o',
        'o̞ː': 'oː',
        'e̞ː': 'eː',
        'e̞': 'e',
        'ẽ̞': 'e',
        'ĩ': 'i',
        'a̠ː': 'aː',
        'a̠': 'a',
        'ã̠': 'a',
        # 'ɯ̟ᵝ': 'ɯ',
        'ɰᵝ': 'w',
        # 'ɯ̟̊ᵝ': 'ɨ̥',
        # 'ɯ̟ᵝː': 'ɨː',
        # 'ɯ̟̃ᵝ': 'ɨ',
        # 'ɨ̥ᵝ': 'ɨ̥',
        # 'ɨᵝ': 'ɨ',
        # 'ɨ̃ᵝ': 'ɨ',
        # 'ɨᵝː': 'ɨː',
        'ɲ̟': 'ɲ',
        'ŋʲ': 'ɲ',
        'p̚ʲ': 'p̚',
        'k̚ʲ': 'k̚',
        't̚ʲ': 't̚',
    },
    'turkish': {
        'ɑ': 'a',
        'ɑː': 'aː',
        'ɛ': 'e',
        'e̞': 'e',
        'ɔ': 'o',
        'ʊ': 'u',
        'ʏ': 'y',
        'o̞': 'o',
        'ɪ': 'i',
        'ø': 'œ',
        'ɾ̝̊': 'ɾ',

    },
    'korean_hangul': {
        'a̠': 'a',
        'e̞': 'e',
        'e̞ː': 'eː',
        'a̠ː': 'a',
        'o̞': 'o',
        'o̞ː': 'oː',
        'ʌ̹': 'ʌ',
        'ɘː': 'ʌː',
        'ɦ': 'h',
        'ɸʷ': 'ɸ',
        'ʃʰ': 'sʰ',

    },
    'english_uk': {
        'ɝː': 'ɜː',
        'əː': 'ɜː',
        'æː': 'æ',
        'ɝ': 'ɜ',
        'ɚ': 'ə',
        'ɫ': 'l',
        'r': 'ɹ',
        'ʍ': 'w',

    },
    'english_us': {
        'ɫ': 'l',
        'r': 'ɹ',
        'ʍ': 'w',
        'æː': 'æ',

    },

}


def convert_language_specific(word, phones, lang):
    new_pron = []
    if lang == 'swedish':
        for i, p in enumerate(phones):
            if p == '¹':
                found_first = False
                found_second = False
                for j in range(i + 1, len(phones)):
                    if phones[j] in vowels[lang]:
                        if not found_first:
                            phones[j] += '˥˧'  # Falling tone
                            found_first = True
                        elif not found_second:
                            phones[j] += '˩'  # Low tone
                            found_second = True
                        else:
                            break
                continue
            elif p == '²':
                found_first = False
                found_second = False
                for j in range(i + 1, len(phones)):
                    if phones[j] in vowels[lang]:
                        if not found_first:
                            phones[j] += '˧˩'  # Falling tone
                            found_first = True
                        elif not found_second:
                            phones[j] += '˥˩'  # Falling tone
                            found_second = True
                        else:
                            break
                continue
            new_pron.append(p)
        phones = new_pron
    new_pron = []
    for i, p in enumerate(phones):
        if lang == 'english_us':
            if lang in lang_mapping:
                for k, v in lang_mapping[lang].items():
                    if p == k:
                        p = v
                        break

            if p == 'ʒ' and len(new_pron) and new_pron[-1] == 'd':  # fix up affricates being split
                new_pron[-1] = 'dʒ'
                continue
            elif p == 'ʃ' and len(new_pron) and new_pron[-1] == 't':  # fix up affricates being split
                new_pron[-1] = 'tʃ'
                continue
            elif p in ['ɪ', 'j'] and len(new_pron) and new_pron[-1] in {'e', 'ɔ', 'o'}:
                new_pron[-1] += 'ɪ'
                continue
            elif p in {'ʊ', 'u'} and len(new_pron) and new_pron[-1] in {'a', 'ɑ', 'ʌ'}:
                new_pron[-1] = 'aʊ'
                continue
            elif p in ['ɪ', 'j'] and len(new_pron) and new_pron[-1] in {'a', 'ɑ', 'ʌ'}:
                new_pron[-1] = 'aɪ'
                continue
            elif p in {'ʊ', 'u'} and len(new_pron) and new_pron[-1] in {'ə', 'o', 'ɔ'}:
                new_pron[-1] = 'oʊ'
                continue
            elif p in {'ɹ', 'ɚ'} and len(new_pron) and new_pron[-1] in {'o', 'ɔ'}:
                new_pron[-1] = 'ɔ'
                p = 'ɹ'
            elif p in {'ɹ', 'ɚ'} and len(new_pron) and new_pron[-1] in {'i', 'ɪː', 'ɪ'}:
                new_pron[-1] = 'ɪ'
                p = 'ɹ'
            elif p in {'ɹ', 'ɚ'} and len(new_pron) and new_pron[-1] in {'u', 'ʊ'}:
                new_pron[-1] = 'ʊ'
                p = 'ɹ'
            elif p in {'ɹ', 'ɚ'} and len(new_pron) and new_pron[-1] in {'e', 'ɛ', 'ɛː', 'æ', 'æː'}:
                new_pron[-1] = 'ɛ'
                p = 'ɹ'
            elif p == 'ɹ' and len(new_pron) and new_pron[-1] in ['ɜ', 'ɜː']:
                new_pron[-1] = 'ɝ'
                continue
            elif p == 'ɹ' and len(new_pron) > 1 and new_pron[-1] == 'ə' and new_pron[-2] in {'ɪ', 'i', 'ɪː'}:
                new_pron[-1] = 'ɹ'
                new_pron[-2] = 'ɪ'
                continue
            elif p == 'ɹ' and len(new_pron) > 1 and new_pron[-1] == 'ə' and new_pron[-2] in {'ʊ', 'u'}:
                new_pron[-1] = 'ɹ'
                new_pron[-2] = 'ʊ'
                continue
            elif p == 'ɹ' and len(new_pron) > 1 and new_pron[-1] == 'ə' and new_pron[-2] in {'e', 'ɛ', 'ɛː'}:
                new_pron[-1] = 'ɹ'
                new_pron[-2] = 'ɛ'
                continue
            elif p == 'w' and len(new_pron) and new_pron[-1] == 'h':  # get rid of h w sequences
                new_pron[-1] = 'w'
                continue
            elif p in {'k', 'ɡ'} and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'ŋ'
                continue
            elif p in {'ɜ', 'ɜː'} and (i == len(phones) - 1 or phones[i + 1] != 'ɹ'):
                p = 'ɝ'
            elif p == 'ɪ' and i == len(phones) - 1:
                p = 'i'
            elif p == 'l' and len(new_pron) and new_pron[-1] == 'ə' and i == len(phones) - 1:  # final syllabic l's
                new_pron[-1] = 'l̩'
                continue
            elif p == 'm' and len(new_pron) and new_pron[-1] == 'ə' and i == len(phones) - 1:  # final syllabic m's
                new_pron[-1] = 'm̩'
                continue
            elif p == 'n' and len(new_pron) and new_pron[-1] == 'ə' and i == len(phones) - 1:  # final syllabic n's
                new_pron[-1] = 'n̩'
                continue
            elif p == 'ɹ' and len(new_pron) and new_pron[-1] == 'ə' and i == len(phones) - 1:  # final syllabic r's
                new_pron[-1] = 'ɚ'
                continue
            elif p == 'ŋ' and i == len(phones) - 1 and new_pron[-1] == 'i':
                new_pron[-1] = 'ɪ'
                continue
        elif lang == 'english_uk':
            if lang in lang_mapping:
                for k, v in lang_mapping[lang].items():
                    if p == k:
                        p = v
                        break
            if p == 'ɹ' and i == len(phones) - 1:
                continue
            elif p == 'ɪ' and i == len(phones) - 1:
                p = 'i'
            elif p in {'l', 'm', 'n'} and i == len(phones) - 1 and len(new_pron) and new_pron[-1] in {'ə', 'əː'}:
                new_pron[-1] = p + '̩'
                continue
            elif p == 'ɪ' and len(new_pron) and new_pron[-1] in {'e', 'a', 'ɔ', 'o'}:
                new_pron[-1] = new_pron[-1] + p
                continue
            elif p == 'ʊ' and len(new_pron) and new_pron[-1] in {'e', 'a'}:
                new_pron[-1] = new_pron[-1] + p
                continue
            elif p in {'ʊ', 'u'} and len(new_pron) and new_pron[-1] in {'ə', 'o', 'ɔ'}:
                new_pron[-1] = 'oʊ'
                continue
            elif p == 'ʒ' and len(new_pron) and new_pron[-1] == 'd':  # fix up affricates being split
                new_pron[-1] = 'dʒ'
                continue
            elif p == 'ʃ' and len(new_pron) and new_pron[-1] == 't':  # fix up affricates being split
                new_pron[-1] = 'tʃ'
                continue
            elif p == 'w' and len(new_pron) and new_pron[-1] == 'h':  # get rid of h w sequences
                new_pron[-1] = 'w'
                continue
            elif p in {'k', 'ɡ'} and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'ŋ'
                continue
            elif p == 'ə' and len(new_pron) and new_pron[-1] == 'ɛ':
                new_pron[-1] = 'ɛː'
                continue
            elif p == 'ŋ' and i == len(phones) - 1 and new_pron[-1] == 'i':
                new_pron[-1] = 'ɪ'
                continue
            elif p == 'ɹ' and len(new_pron) > 2 and new_pron[-1] == 'ə' and new_pron[-2] in {'e', 'ɛ', 'ʊ', 'ɪ', 'ɪː', 'ɛː'}:
                new_pron[-1] = p
                continue
        elif lang == 'bulgarian':
            if p in {'s', 'ʃ', 'sʲ'} and len(new_pron) and new_pron[-1] == 't':
                new_pron[-1] += p
                continue
            elif p == 'ʒ' and len(new_pron) and new_pron[-1] == 'd':
                new_pron[-1] = 'dʒ'
                continue
        elif lang == 'czech':
            if p == 'ɫ':
                p = 'l'  # just use light l
            elif p == 'r̝̊':
                p = 'r̝'
            elif p == 'ɾ':
                p = 'r'
            elif p == 'ɔ':  # Standard variety version
                p = 'o'
            elif p == 'ɔː':  # Standard variety version
                p = 'oː'
            elif p in {'u', 'ʊ'} and len(new_pron) and new_pron[-1] in {'o', 'ɔ'}:
                new_pron[-1] = 'ou'
                continue
            elif p in ['u', 'ʊ'] and len(new_pron) and new_pron[-1] in {'a'}:
                new_pron[-1] = 'au'
                continue
            elif p in {'u', 'ʊ'} and len(new_pron) and new_pron[-1] in {'e', 'ɛ'}:
                new_pron[-1] = 'au'
                continue
            elif p in {'ʃ', 's'} and len(new_pron) and new_pron[-1] in {'t'}:
                new_pron[-1] += p
                continue
            elif p in {'ʒ'} and len(new_pron) and new_pron[-1] in {'d'}:
                new_pron[-1] += p
                continue
            elif p == 'ʊ':
                p = 'u'
            elif p == 'e':
                p = 'ɛ'
        elif lang == 'croatian':
            if p == 'ɕ' and len(new_pron) and new_pron[-1] == 't':
                new_pron[-1] = 'tɕ'
                continue
            elif p == 'ʑ' and len(new_pron) and new_pron[-1] == 'd':
                new_pron[-1] = 'dʑ'
                continue
        elif lang == 'german':
            if p in {'ʏ', 'ɪ'} and len(new_pron) and new_pron[-1] in {'o', 'ɔ'}:
                new_pron[-1] = 'ɔʏ'
                continue
            elif p == 'ɪ' and len(new_pron) and new_pron[-1] == 'a':
                new_pron[-1] = 'aɪ'
                continue
            elif p == 'ɪ' and len(new_pron) and new_pron[-1] == 'ʊ':
                new_pron[-1] = 'ʊɪ'
                continue
            elif p == 'ʊ' and len(new_pron) and new_pron[-1] == 'a':
                new_pron[-1] = 'aʊ'
                continue
            elif p == 'e' and len(new_pron) and new_pron[-1] == 'ɐ':
                new_pron[-1] = 'ɐ'
                continue
            elif p == 's' and len(new_pron) and new_pron[-1] == 't':
                if 'z' in word or 'c' in word:
                    new_pron[-1] = 'ts'
                    continue
            elif p == 'õ':
                new_pron.append('o')
                new_pron.append('n')
                continue
            elif p == 'ɛ̃':
                new_pron.append('eː')
                new_pron.append('n')
                continue
        elif lang == 'mandarin_hani':
            vowel_pattern = re.compile(r'^[ayeiouəɚʊɤ̃]+[²³⁰¹⁴⁵]*$')
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
            if p in {'²', '³', '¹', '⁰', '⁴', '⁵', '⁻', '⁽', '⁾'} and len(new_pron):
                index = -1
                for j in range(len(new_pron) - 1, -1, -1):
                    if vowel_pattern.match(new_pron[j]) or '̩' in new_pron[j]:
                        index = j
                        break
                if new_pron[index].endswith('²¹⁴'):
                    continue
                new_pron[index] += p
                continue
            elif p.startswith('ˀ'):
                new_pron.append('ʔ')
                if p[1] in lang_mapping[lang]:
                    new_pron.append(lang_mapping[lang][p[1]])
                else:
                    new_pron.append(p[1])
                continue
            elif any(p.startswith(x) for x in vowels[lang]) and len(new_pron) and re.match(r'^[ayeiouəɚʊɤ̃]+$', new_pron[-1]):
                new_pron[-1] += p
                continue
        elif lang == 'portuguese_brazil':
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
            if p == 'w̃' and len(new_pron) and new_pron[-1] in {'ɐ̃', 'õ'}:
                new_pron[-1] += p
                continue
            elif p == 'j̃' and len(new_pron) and new_pron[-1] in {'ɐ̃', 'õ', 'ẽ', "ũ"}:
                new_pron[-1] += p
                continue
            elif p == 'j' and len(new_pron) and new_pron[-1] in {'a', 'ɛ', 'e', 'ɐ', 'ɔ', 'o', 'u'}:
                new_pron[-1] += p
                continue
            elif p == 'w' and len(new_pron) and new_pron[-1] in {'a', 'ɛ', 'e', 'ɐ', 'i'}:
                new_pron[-1] += p
                continue
        elif lang == 'portuguese_portugal':
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
            if p == 'w̃' and len(new_pron) and new_pron[-1] in {'ɐ̃', 'õ'}:
                new_pron[-1] += p
                continue
            elif p == 'j̃' and len(new_pron) and new_pron[-1] in {'ɐ̃', 'õ', 'ẽ', "ũ"}:
                new_pron[-1] += p
                continue
            elif p == 'j' and len(new_pron) and new_pron[-1] in {'a', 'ɛ', 'e', 'ɐ', 'ɔ', 'o', 'u'}:
                new_pron[-1] += p
                continue
            elif p == 'w' and len(new_pron) and new_pron[-1] in {'a', 'ɛ', 'e', 'ɐ', 'i'}:
                new_pron[-1] += p
                continue
        elif lang == 'swedish':
            if p == 'ʒ' and len(new_pron) and new_pron[-1] == 'd':
                new_pron[-1] += p
                continue
            elif p == 'aʊ':
                new_pron.append('a')
                new_pron.append('ʊ')
                continue
            elif p in {'r', 'n', 'l', 't', 'k', 'ɡ'} and len(new_pron) and new_pron[-1] == 'ə':
                new_pron[-1] = 'ɛ'
            elif p == 'ə' and i == len(phones) - 1:
                p = 'e'
            elif p in {'r'} and len(new_pron) and new_pron[-1] == 'ɜ':
                new_pron[-1] = 'æː'
            elif p == 'ɜ' and i == len(phones) - 1:
                p = 'e'
        elif lang == 'tamil':
            if p in {'ʊ', 'ɪ'} and len(new_pron) and new_pron[-1] == 'a':
                new_pron[-1] += p
                continue
        elif lang in ['spanish_castilian', 'spanish_latin_america']:
            if p in {'x', 'k', 'ɡ'} and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'ŋ'
            elif p in {'ɟʝ', 'j'} and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'ɲ'
            elif p in {'β', 'b', 'p', } and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'm'
        elif lang == 'thai':
            if p in {'j', 'w'} and len(new_pron) and new_pron[-1] in {'a', 'aː'}:
                new_pron[-1] += p
                continue
            if p in {'a'} and len(new_pron) and new_pron[-1] in {'i', 'iː', 'ɯ', 'ɯː', 'u', 'uː'}:
                new_pron[-1] += p
                continue
            if p in {'w'} and len(new_pron) and new_pron[-1] in {'e', 'eː', 'ɛ', 'ɛː', 'ia'}:
                new_pron[-1] += p
                continue
            if p in {'j'} and len(new_pron) and new_pron[-1] in {'ɤ', 'ɤː', 'o', 'oː', 'ɔ', 'ɔː', 'ɯa', 'ua'}:
                new_pron[-1] += p
                continue
        elif lang == 'turkish':
            if p == 'ʃ' and len(new_pron) and new_pron[-1] in {'t'}:
                new_pron[-1] += p
                continue
            elif p == 'ʒ' and len(new_pron) and new_pron[-1] in {'d'}:
                new_pron[-1] += p
                continue
        elif lang == 'portuguese_brazil':
            if p == 'ʃ' and len(new_pron) and new_pron[-1] in {'t'}:
                new_pron[-1] += p
                continue
            elif p == 'ʒ' and len(new_pron) and new_pron[-1] in {'d'}:
                new_pron[-1] += p
                continue
        elif lang == 'japanese':
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
            if p in {'p', 'pʲ'} and len(new_pron) and new_pron[-1] in {'p̚'}:
                new_pron[-1] = p + 'ː'
                continue
            elif p in {'k', 'kʲ'} and len(new_pron) and new_pron[-1] in {'k̚'}:
                new_pron[-1] = p + 'ː'
                continue
            elif p in {'t', 'tʲ'} and len(new_pron) and new_pron[-1] in {'t̚'}:
                new_pron[-1] = p + 'ː'
                continue
            elif p in {'tɕ', 'ts'} and len(new_pron) and new_pron[-1] in {'t̚'}:
                new_pron[-1] = p + 'ː'
                continue
            elif p in {'i', 'iː', 'i̥'} and len(new_pron) and 'ʲ' in new_pron[-1]:
                if len(new_pron) > 2 and 'ʲ' in new_pron[-2]:
                    new_pron[-2] = new_pron[-2].replace('ʲ', '')

                new_pron[-1] = new_pron[-1].replace('ʲ', '')
            elif p in {'i'} and len(new_pron) and new_pron[-1] == 'n':
                new_pron[-1] = 'ɲ'
            elif False and p in {'k', 'ɡ'} and len(new_pron) and new_pron[-1] == 'ɲ':
                new_pron[-1] = 'ŋ'
            elif False and p in {'t', 'd'} and len(new_pron) and new_pron[-1] == 'ɲ':
                new_pron[-1] = 'n'
            elif p in {'dz', 'dʑ'} and len(new_pron) and new_pron[-1] not in {'ɲ', 'n'}:
                p = p[1]
            elif p in {'ɯ̟̃ᵝ', 'ɯ̟̊ᵝ', 'ɯ̟ᵝː', 'ɯ̟ᵝ', 'ɨ̥ᵝ', 'ɨᵝ', 'ɨ̃ᵝ', 'ɨᵝː', 'ɨ̥', 'ɨ̥ː', 'ɯ̥ː', 'ɯ̥'}:
                if len(new_pron) and new_pron[-1] in {'t', 'tː', 's', 'sː', 'z', 'zː', 'ɲː',
                                                      'ɲ', 'ç', 'çː', 'n', 'nː', 'ts', 'tsː',
                                                      'ɕ', 'tɕ', 'tɕː', 'ʑ', 'ɕː', 'ʑː',
                                                      'ɡʲ', 'ɡʲː', 'kʲ', 'kʲː', 'bʲ', 'bʲː', 'pʲ',
                                                      'pʲː', 'mʲ', 'mʲː', 'ɾʲː', 'ɾʲ', 'j'}:
                    new_p = 'ɨ'
                else:
                    new_p = 'ɯ'
                if '̥' in p or '̊' in p:
                    new_p += '̥'
                if 'ː' in p:
                    new_p += 'ː'
                p = new_p
                if len(new_pron) and new_pron[-1] == 'n':
                    new_pron[-1] = 'ɲ'

        elif lang == 'korean_hangul':
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
            if p in {'e', 'ɛː', 'ɛ', 'a', 'o', 'u', 'ʌ'} and len(new_pron) and new_pron[-1] in {'j'}:
                new_pron[-1] += p
                continue
            elif p in {'i'} and len(new_pron) and new_pron[-1] in {'w', 'ɥ'}:
                new_pron[-1] = 'ɥi'
                continue
            elif p in {'e', 'ɛː', 'ɛ', 'a', 'o', 'i', 'ʌ'} and len(new_pron) and new_pron[-1] in {'w'}:
                new_pron[-1] += p
                continue
            elif p in {'i'} and len(new_pron) and new_pron[-1] in {'ɰ'}:
                new_pron[-1] += p
                continue
            elif p == 't͈' and 'ᄄ' not in jamo.h2j(word):
                if len(new_pron) and '̚' in new_pron[-1]:
                    p = 'tʰ'
                else:
                    p = 't'
            elif p == 'tɕ͈' and 'ᄍ' not in jamo.h2j(word):
                if len(new_pron) and '̚' in new_pron[-1]:
                    p = 'tɕʰ'
                else:
                    p = 'tɕ'
            elif p == 'k͈' and 'ᄁ' not in jamo.h2j(word):
                if len(new_pron) and '̚' in new_pron[-1]:
                    p = 'kʰ'
                else:
                    p = 'k'
            elif p == 'p͈' and 'ᄈ' not in jamo.h2j(word):
                if len(new_pron) and '̚' in new_pron[-1]:
                    p = 'pʰ'
                else:
                    p = 'p'
            elif p == 's͈' and 'ᄊ' not in jamo.h2j(word):
                if len(new_pron) and '̚' in new_pron[-1]:
                    p = 'sʰ'
                else:
                    p = 's'

        elif lang in ['vietnamese_hanoi', 'vietnamese_hue', 'vietnamese_hochiminhcity']:
            vowel_pattern = re.compile(rf'^[{"".join(vowels[lang])}]+$')
            if p in {'j', 'w'} and len(new_pron) and vowel_pattern.match(new_pron[-1]):
                new_pron[-1] += p
                continue
        if lang in lang_mapping:
            for k, v in lang_mapping[lang].items():
                if p == k:
                    p = v
                    break
        if not p:
            continue
        new_pron.append(p)
    tone_mapping = {
        '⁰': '',
        '¹': '˩',
        '²': '˨',
        '³': '˧',
        '⁴': '˦',
        '⁵': '˥',
        '˧': '˧',
        '˨˩': '˨˩',
        '˥˩': '˥˩',
        '˦˥': '˦˥',
        '˩˩˦': '˩˩˦',
    }
    if lang == 'thai':
        phones = new_pron
        new_pron = []
        tone_symbols = {'˥˩', '˦˥', '˧', '˨˩', '˩˩˦'}
        for i, p in enumerate(phones):
            if p in tone_symbols:
                for j in range(len(new_pron) - 1, 0, -1):
                    if new_pron[j] in vowels[lang]:
                        new_pron[j] += tone_mapping[p]
                        break
            else:
                new_pron.append(p)
        # split off tone for G2P
        # for i, p in enumerate(new_pron):
        #    for tone in tone_mapping:
        #        if p.endswith(tone):
        #            new_pron[i] = p.replace(tone, ' ') + tone


    elif lang in ['vietnamese_hanoi', 'vietnamese_hue', 'vietnamese_hochiminhcity']:
        phones = new_pron
        new_pron = []
        vowel_pattern = re.compile(rf'^[{"".join(vowels[lang])}]+[wj]?$')
        tone_symbols = {'˦ˀ˥', '˧˦', '˧˧', '˧˨', '˧˩', '˨˩', '˦˧˥', '˦˩', '˧˧', '˧˨', '˨˩', '˨˩˦', '˦˥', '˨˩˨'}
        for i, p in enumerate(phones):
            if p in tone_symbols:
                for j in range(len(new_pron) - 1, 0, -1):
                    if vowel_pattern.match(new_pron[j]):
                        new_pron[j] += p
                        break
            else:
                new_pron.append(p)
    elif lang == 'mandarin_hani':
        mapping = {
            '²¹⁴': '˨˩˦',
            '⁵⁵': '˥˥',
            '³⁵': '˧˥',
            '⁵¹': '˥˩',
            '⁰': '',
        }
        tone_symbols = {'²', '³', '¹', '⁴', '⁵', '⁰'}
        for i, p in enumerate(new_pron):
            if any(x in p for x in tone_symbols):
                for k, v in mapping.items():
                    if k in new_pron[i]:
                        new_pron[i] = new_pron[i].replace(k, v)
            if any(x in new_pron[i] for x in tone_symbols):
                return None
    elif lang == 'swedish':
        for i, p in enumerate(new_pron):
            if p == 'êː':
                new_pron[i] = 'eː˧˩'
            elif p == 'ɛ̂':
                new_pron[i] = 'ɛ˧˩'
            elif p == 'ɵ̂':
                new_pron[i] = 'ɵ˧˩'
            elif p == 'ʉ̂ː':
                new_pron[i] = 'ʉː˧˩'
            elif p == 'ʉ̟ː˥˩':
                new_pron[i] = 'ʉː˥˩'
            elif p == 'ʉ̟ː˧˩':
                new_pron[i] = 'ʉː˧˩'
            elif p == 'ø̀ː':
                new_pron[i] = 'øː˩'
            elif p == 'ɑ̀ː':
                new_pron[i] = 'ɑː˩'
            elif p == 'ỳː':
                new_pron[i] = 'yː˩'
            elif p == 'ỳː˧˩':
                new_pron[i] = 'yː˧˩'

    elif lang == 'hausa':
        phone_mapping = {
            'á': 'a', 'áː': 'aː', 'é': 'e', 'éː': 'eː', 'í': 'i', 'íː': 'iː', 'ó': 'o', 'óː': 'oː', 'úː': 'uː',
            'à': 'a', 'àː': 'aː', 'è': 'e', 'èː': 'eː', 'ì': 'i', 'ìː': 'iː', 'ò': 'o', 'òː': 'oː', 'ùː': 'uː',
            'â': 'a', 'âː': 'aː', 'ê': 'e', 'êː': 'eː', 'î': 'i', 'îː': 'iː', 'ô': 'o', 'ôː': 'oː', 'ûː': 'uː',
        }
        for i, p in enumerate(new_pron):
            if p in {'á', 'áː', 'é', 'éː', 'í', 'íː', 'ó', 'óː', 'úː'} or '́' in p:  # High tone
                if p in phone_mapping:
                    new_pron[i] = phone_mapping[p]
                else:
                    new_pron[i] = p.replace('́', '')
                new_pron[i] += '˥'
            elif p in {'à', 'àː', 'è', 'èː', 'ì', 'ìː', 'ò', 'òː', 'ùː'} or '̀' in p:  # Low tone
                if p in phone_mapping:
                    new_pron[i] = phone_mapping[p]
                else:
                    new_pron[i] = p.replace('̀', '')
                new_pron[i] += '˩'
            elif p in {'â', 'âː', 'ê', 'êː', 'î', 'îː', 'ôː', 'ûː', } or '̂' in p:  # Falling tone
                if p in phone_mapping:
                    new_pron[i] = phone_mapping[p]
                else:
                    new_pron[i] = p.replace('̂', '')
                new_pron[i] += '˥˦'

    return new_pron

def convert_second_round(word, phones, lang):
    if lang not in ['english_us', 'english_uk']:
        return phones
    new_pron = []
    stressed_vowels = {}
    if lang == 'english_uk':
        stressed_vowels = {'aɪ', 'aʊ', 'eɪ', 'i', 'iː', 'oɪ', 'oʊ', 'u', 'uː', 'æ', 'ɑ', 'ɑː', 'ɒ', 'ɔ', 'ɔɪ', 'ɔː','ɛ', 'ɛː', 'ɜ', 'ɜː', 'ʊ', 'ʌ', }
    elif lang == 'english_us':
        stressed_vowels = {'aɪ', 'aʊ', 'eɪ', 'i', 'iː', 'oɪ', 'oʊ', 'u', 'uː', 'æ',  'ɑ', 'ɑː', 'ɔ', 'ɔɪ', 'ɔː', 'ɛ', 'ɝ', 'ɝː', 'ʊ', 'ʌ',}
    all_syllabics = {'ɪ', 'ə', 'ɚ', 'n̩', 'm̩', 'l̩', 'ɫ̩'} | vowels[lang]
    for i, p in enumerate(phones):
        if lang in ['english_us', 'english_uk']:
            if p == 'l'  and 2 < i < len(phones) - 1 and new_pron[-1] == 'ə' and phones[i+1] not in all_syllabics:
                new_pron[-1] = 'ɫ̩'
                continue
            elif p == 'm'  and 2 < i < len(phones) - 1 and new_pron[-1] == 'ə' and phones[i+1] not in all_syllabics:
                new_pron[-1] = 'm̩'
                continue
            elif p == 'n'  and 2 < i < len(phones) - 1 and new_pron[-1] == 'ə' and phones[i+1] not in all_syllabics:
                new_pron[-1] = 'n̩'
                continue
            elif p == 'l̩' and 1 < i < len(phones) - 1 and phones[i+1] in all_syllabics:
                new_pron.append('ə')
                p = 'l'
            elif p == 'l̩':
                p = 'ɫ̩'
            elif p == 'l' and i == len(phones) - 1:
                p = 'ɫ'
            elif p == 'l' and 1 < i < len(phones) - 1 and phones[i+1] not in all_syllabics:
                p = 'ɫ'
            elif p in {'t', 'p', 'k'} and i == 0 and i < len(phones) - 1 and phones[i+1] in stressed_vowels | {'ɪ', 'ə', 'ɚ'}:
                p += 'ʰ'
            elif p == 'ə' and 1 < i == len(phones)-2 and phones[i-1]in {'d', 't'}  and phones[i+1] == 'd':
                p = 'ɪ'
            elif p == 'ə' and 1 < i == len(phones)-2 and phones[i-1] in {'s','z', 'ʃ', 'ʒ', 'tʃ', 'dʒ'} and phones[i+1] == 'z':
                p = 'ɪ'
        if lang == 'english_us':
            if p == 'ɹ'  and 2 < i < len(phones) - 1 and new_pron[-1] == 'ə' and phones[i+1] not in all_syllabics:
                new_pron[-1] = 'ɚ'
                continue
            elif p in {'d', 't'} and 1 < i < len(phones) - 1 and phones[i-1] in all_syllabics and phones[i + 1] in {'n̩', 'm̩', 'l̩', 'ɚ', 'ə', 'ɫ̩'}:
                p ='ɾ'
            elif p in {'t', 'd'}  and 1 < i < len(phones) - 2 and phones[i-1] in all_syllabics and phones[i + 1] == 'ɪ' and phones[i+2] == 'd':
                p ='ɾ'
            elif p in {'t', 'd'} and i > 1 and i == len(phones) - 2 and phones[i-1] in all_syllabics and phones[i+1] == 'i':
                p ='ɾ'
            elif p in {'t', 'd'} and i > 1 and i == len(phones) - 3 and phones[i-1] in all_syllabics and phones[i+1] in {'i', 'ɪ'} and phones[i+2] == 'z':
                p ='ɾ'
            elif p in {'t', 'd'} and i > 1 and i == len(phones) - 3 and phones[i-1] in all_syllabics and phones[i+1] == 'ɪ' and phones[i+2] == 'ŋ':
                p ='ɾ'
            elif p in {'t', 'p', 'k'} and i == 0 and i < len(phones) - 1 and phones[i+1] in stressed_vowels | {'ɪ', 'ə', 'ɚ'}:
                p += 'ʰ'
            elif p in {'t', 'p', 'k'} and i > 0 and phones[i-1] not in  {'s', 'ʃ'} and i < len(phones) - 1 and phones[i+1] in stressed_vowels:
                p += 'ʰ'
            elif p == 'l̩' and 1 < i < len(phones) - 1 and phones[i+1] in all_syllabics:
                new_pron.append('ə')
                p = 'l'
            elif p == 'l̩':
                p = 'ɫ̩'
            elif p == 'l' and i == len(phones) - 1:
                p = 'ɫ'
            elif p == 'l' and 1 < i < len(phones) - 1 and phones[i+1] not in {'ɪ', 'ə', 'ɚ', 'n̩', 'm̩', 'l̩', 'ɫ̩'} | vowels[lang]:
                p = 'ɫ'
            elif p == 'ə' and 1 < i == len(phones)-2 and phones[i-1]in {'d', 't', 'ɾ'}  and phones[i+1] == 'd':
                p = 'ɪ'
            elif p == 'ə' and 1 < i == len(phones)-2 and phones[i-1] in {'s','z', 'ʃ', 'ʒ', 'tʃ', 'dʒ'} and phones[i+1] == 'z':
                p = 'ɪ'
            elif p in {'t', 'p', 'k'} and i > 0 and phones[i-1] not in  {'s', 'ʃ'} and i < len(phones) - 1 and phones[i+1] in stressed_vowels:
                p += 'ʰ'
        elif lang == 'english_uk':
            if p not in vowels[lang] and len(new_pron) and new_pron[-1] == 'ɹ':
                new_pron[-1] = p
                continue
            elif p in {'t', 'p', 'k'} and i > 0 and phones[i-1] not in  {'s', 'ʃ'} and i < len(phones) - 1 and phones[i+1] in stressed_vowels:
                p += 'ʰ'
        new_pron.append(p)
    return new_pron

def check_language_specific(word, phones, lang):
    odd_set = {'ɯ̟ᵝ',
               'ɰᵝ',
               'ɰ̃',
               'ɯ̟̊ᵝ',
               'ɯ̟ᵝː',
               'ɯ̟̃ᵝ', }
    if odd_set & set(phones):
        print(word)
        print(phones)


def fix_pronunciations(dictionary, lang):
    filtered_dictionary = []
    for word, pronunciation in dictionary:
        if lang == 'polish':
            if 'ü' in word:
                continue
        for i, p in enumerate(pronunciation):
            if '̯' in p:
                pronunciation[i] = p.replace('̯', '')
            elif '͡' in p:
                pronunciation[i] = p.replace('͡', '')
            elif '‿' in p:
                pronunciation[i] = p.replace('‿', '')
            elif '͜' in p:
                pronunciation[i] = p.replace('͜', '')
            elif 'g' in p:
                pronunciation[i] = p.replace('g', 'ɡ')
        # Language specific conversions
        new_pron = convert_language_specific(word, pronunciation, lang)
        new_pron = convert_second_round(word, new_pron, lang)
        if new_pron is None:
            continue
        check_language_specific(word, new_pron, lang)
        if (word, new_pron) not in filtered_dictionary:
            filtered_dictionary.append((word, new_pron))
    return filtered_dictionary


def process_language(lang):
    print('Processing', lang)
    if lang == 'japanese':
        dictionary, input_graphemes, input_phones = read_source(lang + '_hiragana')
        d, g, p = read_source(lang + '_katakana')
        dictionary.extend(d)
        input_graphemes.update(g)
        input_phones.update(p)
    else:
        dictionary, input_graphemes, input_phones = read_source(lang)

    print('Input graphemes', sorted(input_graphemes))
    print('Input phones', sorted(input_phones))
    filtered = fix_pronunciations(dictionary, lang)
    save_dictionary(filtered, lang)


if __name__ == '__main__':
    for code in lang_codes:
        process_language(code)
