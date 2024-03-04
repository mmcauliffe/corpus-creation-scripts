import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\spanish'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'lab')

word_set = collections.Counter()

bad_chars = {}

lang = 'es'
period_name = 'punto'

number_pattern = re.compile(r'(?P<number>\d+)(?P<suffix>.*)')

clitic_items ={
}

subs = {
    'del96': 'del 96',
    'del95': 'del 95',
    'M16': 'M 16',
    'm2': 'm 2',
    'siglo XVIII': 'siglo dieciocho',
    'siglo XVII': 'siglo decimoséptimo',
    'Luis XVI': 'Luis el decimosexto',
    'Carlos I': 'Carlos el primero',
    'XXVII Cumbre': 'vigésima séptima Cumbre',
    'VIII Congreso': 'octavo Congreso',
    'XIX': '19',
    'XV': '15',
    'jerusalén': 'jerusalém',
    'XX': '20',
    'XXI': '21',
    'XIII': '13',
    'I Congreso': 'primero Congreso',
    '2/3': 'dos tercios',
    'P I': 'PI',
    '$10473 millones': '10,473 millones dolares',
}

number_mapping = {
}

suffixes = collections.Counter()
if __name__ == '__main__':
    for file in os.listdir(trl_dir):
        speaker_id = os.path.splitext(file)[0]
        path = os.path.join(trl_dir, file)
        output_dir = os.path.join(lab_dir, speaker_id[2:])
        os.makedirs(output_dir, exist_ok=True)
        texts = {}
        current_utterance = 0
        print(file)
        with open(path, 'r', encoding='iso-8859-2') as f:
            for line in f:
                #print(line)
                if 'SprecherID' in line:
                    continue
                if line.startswith(';'):
                    current_utterance += 1
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
                        print(w)
                        #w = re.sub(r'(\d)\.(\d)', r'\1\2', w)
                        #print(w)
                        if not w:
                            continue
                        m = number_pattern.match(w)

                        if m:
                            number = m.group("number")
                            suffix = m.group("suffix")
                            print(number, suffix)
                            print(line)
                            number_type = 'cardinal'
                            #if number in number_mapping:
                            #    converted = number_mapping[number]
                            #else:
                            converted = num2words.num2words(int(number), lang=lang, to=number_type)
                            print(converted)
                            prefix = ''
                            if suffix.startswith('.-'):
                                suffix = suffix[1:]
                            elif suffix == '.':
                                suffix = ''
                            elif suffix.startswith(','):
                                next_number = int(suffix[1:])
                                next_number = num2words.num2words( next_number, lang=lang)
                                suffix = f' {period_name} ' + next_number
                                print(number, suffix)
                            converted = f'{prefix}{converted}{suffix}'
                            print("HELLO", prefix, converted, suffix)
                            converted = converted.replace('cientos', ' cientos').strip()
                            converted = converted.replace('veinti', 'veinti ').strip()
                            print(converted)
                            new_words.append(converted)
                            continue
                        new_words.append(w)
                    print(words)
                    print(new_words)
                    for w in new_words:
                        if (re.search(r'\d', w) and not w.startswith('<')) or 'VII' in w or w == 'I':
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