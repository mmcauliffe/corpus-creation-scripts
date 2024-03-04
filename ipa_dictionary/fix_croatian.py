import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\croatian'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'lab')

word_set = collections.Counter()

bad_chars = {}

number_pattern = re.compile(r'(?P<number>\d+)(?P<suffix>.*)')

clitic_items ={
}

subs = {
    'Falcon-50': 'Falcon 50',
    'C-130': 'C 130',
    'G-222': 'G 222',
    "'96": '96',
    "H323": 'H 323',
    "Rm-2000": 'Rm 2000',
    "CH-53": 'CH 53',
    "A-320": 'A 320',
}

number_mapping = {
    "1":'prv',
    "2":'drug',
    "3":'treć',
    "4":'četvrt',
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
                    current_utterance = int(re.sub(r'[ ;:]', '', line))
                    continue
                else:
                    line = line.strip()
                    if re.search('; \d+:', line):
                        print(file)
                        print(line)
                        error
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
                        w = re.sub(r'(\d)\.(\d)', r'\1\2', w)
                        print(w)
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
                            converted = num2words.num2words(int(number), lang='sr', to=number_type)
                            print(converted)
                            prefix = ''
                            if suffix.startswith('.-'):
                                suffix = suffix[1:]
                            elif suffix == '.':
                                suffix = ''
                            elif suffix.startswith('.') or suffix.startswith(','):
                                m2 = number_pattern.match(suffix[1:])
                                next_number = num2words.num2words( int(m2.group('number')), lang='sr')
                                next_suffix = m2.group('suffix')
                                if not next_suffix.startswith("'"):
                                    next_suffix = ' ' + next_suffix
                                suffix = 'točka ' + next_number + next_suffix
                                print(number, suffix)
                            converted = f'{prefix}{converted}{suffix}'
                            print("HELLO", prefix, converted, suffix)
                            new_words.append(converted)
                            continue
                        new_words.append(w)
                    print(words)
                    print(new_words)
                    for w in new_words:
                        if re.search(r'\d', w) and not w.startswith('<'):
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