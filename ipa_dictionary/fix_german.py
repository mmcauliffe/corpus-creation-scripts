import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\german'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'lab')

word_set = collections.Counter()

bad_chars = {}

lang = 'de'
period_name = 'punkt'

number_pattern = re.compile(r'(?P<number>\d+)(?P<suffix>.*)')

clitic_items ={
}

subs = {
    '5:3-Sieg': '5 zu 3 Sieg',
    '6:4': '6 zu 4',
    '6:3': '6 zu 3',
    '5:3': '5 zu 3',
    '8:2': '8 zu 2',
    '79:57': '79 zu 57',
    '1,3mal': '1,3 mal',
    'G-7-Tagung': 'G 7 Tagung',
    'G-7-Treffen': 'G 7 Treffen',
    'G-7-Ländern': 'G 7 Ländern',
    'G-7-Mitglieder': 'G 7 Mitglieder',
    'GSG-9-Beamte': 'GSG 9 Beamte',
    'Titan-3-Rakete': 'Titan 3 Rakete',
    'SS-24-Systeme': 'SS 24 Systeme',
    'SS-19': 'SS 19',
    "Delors'": 'Delors',
    "Volke!'": 'Volke',
    ",einen": 'einen',
    "Abschied'": 'Abschied',
    "Simonis'": 'Simonis',
    ",Ja'": 'Ja',
    "Neuhaus'": 'Neuhaus',
    "Grams'": 'Grams',
    "Nilius'": 'Nilius',
    "Sozialismus'": 'Sozialismus',
    ",Petitessen'": 'Petitessen',
    "ß": 'ss',
    'G7-Wirtschaftsgipfel': 'G 7 Wirtschaftsgipfel',
}

number_mapping = {
}

sep_pattern = re.compile(r'und(?!e)')
suffixes = collections.Counter()
if __name__ == '__main__':
    for file in os.listdir(trl_dir):
        speaker_id = os.path.splitext(file)[0]
        path = os.path.join(trl_dir, file)
        output_dir = os.path.join(lab_dir, speaker_id[2:])
        os.makedirs(output_dir, exist_ok=True)
        texts = {}
        print(file)
        current_utterance = 0
        with open(path, 'r', encoding='iso-8859-1') as f:
            for line in f:
                #print(line)
                if 'SprecherID' in line:
                    continue
                if line.startswith(';'):
                    next_utt = int(re.sub(r'[ ;:]', '', line))
                    if next_utt - current_utterance > 1:
                        print(speaker_id, 'SKIPPING', next_utt - current_utterance)
                    current_utterance = next_utt
                    continue
                else:
                    line = line.strip()
                    if not line:
                        continue
                    for c in bad_chars:
                        line = line.replace(c, '')
                    for s in subs:
                        line = line.replace(s, subs[s])
                    words = line.split()

                    #print(line)
                    #print(text)
                    #print(' '.join(words))
                    new_words = []
                    for w in words:
                        if w.startswith(","):
                            w = w[1:]
                        if w.endswith("'"):
                            w = w[:-1]
                        #w = re.sub(r'(\d)\.(\d)', r'\1\2', w)
                        #print(w)
                        if not w:
                            continue
                        m = number_pattern.match(w)
                        #w = w.replace('hundert', ' hundert ')
                        if m:
                            number = m.group("number")
                            suffix = m.group("suffix")
                            number_type = 'cardinal'
                            #if number in number_mapping:
                            #    converted = number_mapping[number]
                            #else:
                            if len(number) == 4 and any(number.startswith(x) for x in ['19','18','17']):
                                converted = num2words.num2words(int(number[:2]), lang=lang, to=number_type)
                                converted += ' hundert '
                                converted += num2words.num2words(int(number[2:]), lang=lang, to=number_type)
                            else:
                                converted = num2words.num2words(int(number), lang=lang, to=number_type)
                                converted = converted.replace('hundert', ' hundert ')
                            converted = sep_pattern.sub(' und ', converted)
                            converted = converted.replace("ß", 'ss')
                            prefix = ''
                            if suffix.startswith('.-'):
                                suffix = suffix[1:]
                            elif suffix == '.':
                                suffix = ''
                            elif suffix.startswith(','):
                                new_suffix = f' komma '
                                for c in suffix[1:]:
                                    new_suffix += num2words.num2words( int(c), lang=lang) + ' '
                                suffix = new_suffix
                            elif suffix.startswith('.'):
                                new_suffix = f' punkt '
                                for c in suffix[1:]:
                                    new_suffix += num2words.num2words( int(c), lang=lang) + ' '
                                suffix = new_suffix
                            converted = f'{prefix}{converted}{suffix}'
                            new_words.append(converted)
                            continue
                        new_words.append(w)
                    for w in new_words:
                        if re.search(r'\d', w) and not w.startswith('<') or w.endswith("'"):
                            print(line)
                            print(w, m)
                            error

                    word_set.update(new_words)
                    if current_utterance not in texts:
                        texts[current_utterance] = new_words
                    else:
                        texts[current_utterance] += new_words
        for utterance, words in texts.items():
            for w in words:
                if "'" in w and ">" not in w:
                    suffixes[("'"+ w.split("'")[-1])] += 1
                if re.search(r'\d', w) and not w.startswith('<'):
                    print(w)
                    print(file)
                    error
            path = os.path.join(output_dir, f'{speaker_id}_{utterance}.lab')
            with open(path, 'w', encoding='utf8') as f:
                f.write(' '.join(words))
for k,v in sorted(word_set.items(), key=lambda x:x[1]):
    print(k, v)

for k,v in sorted(suffixes.items(), key=lambda x:x[1]):
    print(k, v)