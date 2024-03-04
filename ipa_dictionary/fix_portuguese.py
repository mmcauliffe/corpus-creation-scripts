import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\portuguese'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'lab')

word_set = collections.Counter()

bad_chars = {}

lang = 'pt_BR'
period_name = 'ponto'

number_pattern = re.compile(r'(?P<number>\d+)(?P<suffix>.*)')

clitic_items ={
}

subs = {
    '29/05/97': '29 de maio 97',
    'emps97': 'emps 97',
    'Windows95': 'Windows 95',
    'A4': 'A 4',
    '`': '',
    ':': '',
    "misto'": 'misto',
    "crise'": 'crise',
    "confiáveis.'": 'confiáveis',
}

number_mapping = {
}

letter_replacements = {
    'ő': 'õ',
    'ă': 'ã',
    'ę': 'ê',
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
                    line = re.sub(r'(?<!\s)<(?!\s)', ' <', line)
                    line = re.sub(r'(?<!\s)>(?!\s)', '> ', line)

                    for m in re.finditer(r'<[^<>]+?>', line):
                        print(m.group())
                        replacement = m.group().replace(' ', '_')
                        line = line.replace(m.group(), replacement)

                    words = line.split()

                    #print(line)
                    #print(text)
                    #print(' '.join(words))
                    new_words = []
                    for w in words:
                        #w = re.sub(r'(\d)\.(\d)', r'\1\2', w)
                        #print(w)
                        if not w:
                            continue
                        if w.endswith('>') and not w.startswith('<') and len(new_words) and new_words[-1].startswith('<'):
                            new_words[-1] += '_' + w
                        m = number_pattern.match(w)

                        if m:
                            number = m.group("number")
                            suffix = m.group("suffix")
                            number_type = 'cardinal'
                            #if number in number_mapping:
                            #    converted = number_mapping[number]
                            #else:
                            converted = num2words.num2words(int(number), lang=lang, to=number_type)
                            prefix = ''
                            if suffix.startswith('h'):
                                if int(number) == 1:
                                    converted = 'uma'
                                elif int(number) == 2:
                                    converted = 'duas'
                                if len(suffix) == 1:
                                    suffix = ''
                                else:
                                    next_number = int(suffix[1:])
                                    if next_number == '30':
                                        next_number = 'meio' # apparently dialectal
                                    else:
                                        next_number = num2words.num2words( next_number, lang=lang)
                                    suffix = f'e ' + next_number
                            elif suffix == '.':
                                suffix = ''
                            elif suffix.startswith(',') or suffix.startswith('.'):
                                next_number = int(suffix[1:])
                                next_number = num2words.num2words( next_number, lang=lang)
                                suffix = f' {period_name} ' + next_number
                            converted = f'{prefix}{converted}{suffix}'
                            new_words.append(converted)
                            continue
                        new_words.append(w)
                    print(line)
                    print(new_words)
                    for w in new_words:
                        if (re.search(r'\d', w) and not w.startswith('<')) or w.endswith("'") or '>' in w[:-1]:
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
                text = ' '.join(words)
                for k,v in letter_replacements.items():
                    text = text.replace(k, v)
                f.write(text)
for k,v in sorted(word_set.items(), key=lambda x:x[1]):
    print(k, v)

for k,v in sorted(suffixes.items(), key=lambda x:x[1]):
    print(k, v)