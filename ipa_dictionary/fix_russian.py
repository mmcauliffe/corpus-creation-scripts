import collections
import os
import re
import num2words

root = r'D:\Data\speech\GlobalPhone\russian'
trl_dir = os.path.join(root, 'trl')
lab_dir = os.path.join(root, 'files')

word_set = collections.Counter()

bad_chars = {}

lang = 'ru'
period_name = 'punkt'

number_pattern = re.compile(r'(?P<number>\d+)(?P<suffix>.*)')

clitic_items ={
}

subs = {
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
        with open(path, 'r', encoding='koi8-r') as f:
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
                    for i, w in enumerate(words):
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
                                converted = num2words.num2words(int(number), lang=lang, to=number_type)
                                print(current_utterance)
                                if not suffix and i < len(words) - 1:
                                    if words[i+1] == 'году':
                                        suffix = 'ем'
                                    elif file == 'RU060.trl' and current_utterance in {26, 32}:
                                        suffix = 'ем'
                                    elif file == 'RU097.trl' and current_utterance in {141}:
                                        suffix = 'ем'
                                    elif words[i+1] in {'год', 'г'}:
                                        suffix = 'ий'
                                    elif file == 'RU060.trl' and current_utterance in {35}:
                                        suffix = 'ий'
                                    elif file == 'RU097.trl' and current_utterance in {191, 194}:
                                        suffix = 'ий'
                                    elif words[i+1] == 'годах':
                                        print(converted)
                                        suffix = 'ий'
                                        error
                                    elif words[i+1] == 'года':
                                        suffix = 'ого'
                                    elif file == 'RU018.trl' and current_utterance == 17:
                                        pass
                                    elif file == 'RU072.trl' and current_utterance in {36, 37}:
                                        pass
                                    elif file == 'RU081.trl' and current_utterance in {96}:
                                        pass
                                    else:
                                        print(line)
                                        print(w, number, converted+suffix, num2words.num2words(number, lang=lang, to='ordinal'))
                                        error
                            else:
                                converted = num2words.num2words(int(number), lang=lang, to=number_type)
                            prefix = ''
                            percent = suffix.endswith('%')
                            if percent:
                                suffix = suffix[:-1]
                            if suffix.startswith(','):
                                new_suffix = f' запятая '
                                for c in suffix[1:]:
                                    new_suffix += num2words.num2words( int(c), lang=lang) + ' '
                                suffix = new_suffix
                            elif suffix.startswith('.'):
                                new_suffix = f' и '
                                for c in suffix[1:]:
                                    new_suffix += num2words.num2words( int(c), lang=lang) + ' '
                                suffix = new_suffix
                            converted = f'{prefix}{converted}{suffix}'
                            if percent:
                                converted += ' процента'
                            new_words.append(converted)
                            continue
                        if w.isupper():
                            w = ' '.join(w)
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
if False:
    for k,v in sorted(word_set.items(), key=lambda x:x[1]):
        print(k, v)

    for k,v in sorted(suffixes.items(), key=lambda x:x[1]):
        print(k, v)