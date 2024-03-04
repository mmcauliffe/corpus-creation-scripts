import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\swedish'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'lab')

word_set = collections.Counter()

bad_chars = {}

number_pattern = re.compile(r'<#_?(?P<number>[\d_]+)(?P<suffix>.*)>')

clitic_items ={
}

subs = {
    'ettundratio': 'ett hundra tio',
    'ettusenfem': 'ett tusen fem',
    'fyratusenfem': 'fyra tusen fem',
    'fyratusenfyra': 'fyra tusen fyra',
    'niotusentvå': 'nio tusen två',
    'nittontusensju': 'nitton tusen sju',
    'sextusentre': 'sex tusen tre',
    'sjutusennio': 'sju tusen nio',
    'tolvtusenfem': 'tolv tusen fem',
    'tusenfyra': 'tusen fyra',
    'tusenåtta': 'tusen åtta',
    'ettusentre': 'ett tusen tre',
    'ettusensex': 'ett tusen sex',
    'ettusenfyra': 'ett tusen fyra',
    'ettusentvå': 'ett tusen två',
    'ettusenett': 'ett tusen ett',
    'femtusensex': 'fem tusen sex',
    'femtusentvå': 'fem tusen två',
    'ettusensju': 'ett tusen sju',
    'ettusenåtta': 'ett tusen åtta',
    'ettusenåttio': 'ett tusen åttio',
    'ettusentrettio': 'ett tusen trettio',
}

number_replacements = {
    'hundra': ' hundra ',
    'miljon': ' miljon ',
    'tiosex': 'tio sex',
    'tjugosex': 'tjugo sex',
    'tiofyra': 'tio fyra',
    'tjugofyra': 'tjugo fyra',
    'tioett': 'tio ett',
    'tjugoett': 'tjugo ett',
    'tioen': 'tio en',
    'tjugoen': 'tjugo en',
    'tioåtta': 'tio åtta',
    'tjugoåtta': 'tjugo åtta',
    'tiotvå': 'tio två',
    'tiotre': 'tio tre',
    'tjugotvå': 'tjugo två',
    'tjugotre': 'tjugo tre',
    'tiosju': 'tio sju',
    'tjugosju': 'tjugo sju',
    'tiofem': 'tio fem',
    'tionio': 'tio nio',
    'tjugonio': 'tjugo nio',
    'tiotusen': 'tio tusen',
    'tjugotusen': 'tjugo tusen',
    'tjugofem': 'tjugo fem',

}

split_number_patterns = (

            (' hundra ', re.compile(r'hundra')),
        (' tusen ', re.compile(r'tusen')),
                   ('tio ', re.compile(r'tio(?!n)')),
('tio ', re.compile(r'tio(?=nio)$')),
('tjugo ', re.compile(r'tjugo')),
('ett ', re.compile(r'\bet ')),
)



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
                    for rep, pattern in split_number_patterns:
                        line = pattern.sub(rep, line)
                    words = line.split()
                    new_words = []
                    for w in words:
                        if '<' in w[1:] and w[0] != '<':
                            word, num = w.split('<')
                            new_words.append(word)
                            new_words.append('<'+num)
                            continue
                        elif w.endswith('>') and not w.startswith('<'):
                            new_words[-1] += w
                            continue
                        new_words.append(w)
                    words = new_words
                    #print(line)
                    #print(text)
                    #print(' '.join(words))
                    new_words = []
                    for w in words:
                        #w = re.sub(r'(\d)_(\d)', r'\1\2', w)
                        if not w:
                            continue
                        m = number_pattern.match(w)
                        for k, v in number_replacements.items():
                            w = w.replace(k, v)
                        if m:
                            continue
                            number = m.group("number")
                            suffix = m.group("suffix")
                            print(number, suffix)
                            print(line)
                            number_type = 'cardinal'
                            #if number in number_mapping:
                            #    converted = number_mapping[number]
                            #else:
                            if len(number) == 4 and any(number.startswith(x) for x in ['19','18','17']):
                                converted = num2words.num2words(int(number[:2]), lang='sv', to=number_type)
                                converted += ' hundra '
                                converted += num2words.num2words(int(number[2:]), lang='sv', to=number_type)
                            else:
                                converted = num2words.num2words(int(number), lang='sv', to=number_type)

                            prefix = ''
                            if suffix.startswith('.-'):
                                suffix = suffix[1:]
                            elif suffix == '.':
                                suffix = ''
                            elif suffix.startswith('-'):
                                try:
                                    next_number = int(suffix[1:])
                                    next_number = num2words.num2words( next_number, lang='sv')
                                    suffix = 'till ' + next_number
                                except ValueError:
                                    suffix = suffix[1:]
                            elif suffix.startswith(','):
                                next_number = int(suffix[1:])
                                next_number = num2words.num2words( next_number, lang='sv')
                                suffix = 'komma ' + next_number
                            elif suffix.startswith('.'):
                                next_number = int(suffix[1:])
                                next_number = num2words.num2words( next_number, lang='sv')
                                suffix = 'punkt ' + next_number
                            converted = f'{prefix}{converted}{suffix}'
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