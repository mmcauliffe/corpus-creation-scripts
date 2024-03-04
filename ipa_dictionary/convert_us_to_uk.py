

us_ipa_path = r'D:\Data\speech\esports\esports_dict.txt'

uk_ipa_path = r'D:\Data\speech\esports\esports_dict_uk.txt'


def is_vowel(character):
    return character in {'i', 'iː', 'u', 'uː', 'ɪ', 'ʊ', 'eɪ', 'oʊ', 'ɛ', 'ɛː',
                         'ɝ', 'ɝː', 'ʌ', 'ə', 'ɚ', 'ɔ', 'ɔː', 'æ', 'æː', 'ɑ',
                         'ɑː', 'aɪ', 'aʊ', 'ɔɪ'}


dictionary = []

with open(us_ipa_path, 'r', encoding='utf8') as f:
    for line in f:
        line = line.strip()
        line = line.split()
        word = line[0]
        pron = line[1:]
        dictionary.append((word, pron))

new_dictionary = []

for word, pron in dictionary:
    new_pron = []
    keep_pron = None
    for i, phone in enumerate(pron):
        if phone == 'ɚ':
            phone = 'ə'
        elif phone == 'ɝ':
            phone = 'ʌ'  # fixme this should likely be 'ɜː'
        elif phone == 'ɹ':
            if i == len(pron) - 1:
                keep_pron = new_pron + ['ɹ']
            if i == len(pron) - 1 or not is_vowel(pron[i+1]):
                if i != 0 and pron[i-1] in ['ɑː', 'ɑ', 'ɔː', 'ɔ']:
                    if not new_pron[-1].endswith('ː'):
                        new_pron[-1] = new_pron[-1] + 'ː'
                    continue
                phone = 'ə'

        new_pron.append(phone)
    new_dictionary.append((word, new_pron))
    if keep_pron is not None:
        new_dictionary.append((word, keep_pron))
    if 'θ' in new_pron:
        new_new_pron = [x if x != 'θ' else 'f' for x in new_pron]
        new_dictionary.append((word, new_new_pron))

with open(uk_ipa_path, 'w', encoding='utf8') as f:
    for word, pron in new_dictionary:
        f.write('{}\t{}\n'.format(word, ' '.join(pron)))