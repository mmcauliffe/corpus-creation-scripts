import collections
import os
import nagisa
lab_dir = '/mnt/d/Data/speech/GlobalPhone/Japanese/Japanese/labs'
resegmented_lab_dir = '/mnt/d/Data/speech/GlobalPhone/Japanese/Japanese/resegmented'

numeral_mapping ={
}
bad_characters = {}

word_set = collections.Counter()

te_endings = {}
de_endings = {}
nai_endings = {}

combinations = {
}

particles = {}

for speaker in os.listdir(lab_dir):
    speaker_dir = os.path.join(lab_dir, speaker)
    if not os.path.isdir(speaker_dir):
        continue
    speaker_out_dir = os.path.join(resegmented_lab_dir, speaker)
    os.makedirs(speaker_out_dir, exist_ok=True)
    for file_name in os.listdir(speaker_dir):
        if not file_name.endswith('.lab'):
            continue
        with open(os.path.join(speaker_dir, file_name), 'r', encoding='utf8') as f:
            original = f.read().strip()

        text = original.replace(' ', '').replace('<', '＜').replace('>', '＞')
        words = nagisa.tagging(text)
        new_words = []
        for i, w in enumerate(words.words):
            if '％' in w:
                error
            tag = words.postags[i]
            for k,v in numeral_mapping.items():
                if w.lower() == k:
                    w = v
                    break
            if len(new_words) and (new_words[-1].startswith('<') and not new_words[-1].endswith('>')):
                new_words[-1] += w
                continue
            elif '<' in w and not w.startswith('<'):
                x = w.split('<')
                new_words.append(x[0])
                new_words.append('<'+ x[1])
                continue
            elif len(new_words) and new_words[-1].endswith('っ'):
                w = 'っ' + w
                new_words[-1] = new_words[-1][:-1]
            new_words.append(w)
            continue
            if i > 0 and not w.startswith('<'):
                if any(w.startswith(x) for x in ['て', 'た']) and (words.postags[i-1] in ['動詞', '助動詞'] or new_words[-1][-1] in te_endings):
                    new_words[-1] += w
                    continue
                elif w == 'なく' and words.postags[i-1] in ['動詞', '助動詞']:
                    new_words[-1] += w
                    continue
                elif w in ['れ', 'られ'] and words.postags[i-1] in ['動詞']:
                    new_words[-1] += w
                    continue
                elif w in ['ない'] and  new_words[-1][-1] in nai_endings:
                    new_words[-1] += w
                    continue
                elif w in ['で'] and  new_words[-1][-1] in de_endings:
                    new_words[-1] += w
                    continue
                elif w in ['だ'] and  new_words[-1][-1] in {'ん'}:
                    new_words[-1] += w
                    continue
                elif w in ['つ', 'カ月', '月', '日'] and new_words[-1] in {'一', '二', '三', '四', '五', '六', '九','七', '八', '十', '十一', '十二'}:
                    new_words[-1] += w
                    continue
                elif w.startswith('ら') and new_words[-1] == '見':
                    new_words[-1] += w
                    continue
                elif new_words[-1] == 'お':
                    new_words[-1] += w
                    continue
                #elif new_words[-1] in combinations and w in combinations[new_words[-1]]:
                #    new_words[-1] += w
                #    continue
                elif new_words[-1].endswith('わ') and (w.startswith('せ') or w.startswith('れ')):
                    new_words[-1] += w
                    continue
                elif w in particles:
                    new_words[-1] += w
                    continue
                elif new_words[-1].endswith('っ'):
                    new_words[-1] += w
                    continue
                elif w == 'せ' and new_words[-1] == '騒が':
                    new_words[-1] += w
                    continue
                elif w == '的':
                    new_words[-1] += w
                    continue
                elif w == 'せて':
                    new_words[-1] += w
                    continue
            #if i > 0 and tag in ['助動詞', '助詞', '接尾辞'] and words.postags[i-1] in ['動詞', '助動詞', '形容詞', '接尾辞', 'web誤脱']:
            #    new_words[-1] += w
            #    continue
            new_words.append(w)
        new_new_words = [] # second pass
        while True:
            for i, w in enumerate(new_words):
                for k,v in numeral_mapping.items():
                    if w.lower() == k:
                        w = v
                        break
                if i > 0 and not w.startswith('<'):
                    if w.endswith('ため') and len(w) > 2:
                        new_new_words.append(w[:-2])
                        new_new_words.append('ため')
                        continue
                    elif w.endswith('事') and len(w) > 1 and w != '大事':
                        new_new_words.append(w[:-1])
                        new_new_words.append('事')
                        continue
                    elif w in particles:
                        new_new_words[-1] += w
                        continue
                    elif w == 'して' and new_new_words[-1] == 'と':
                        new_new_words[-1] += w
                        continue
                    elif w == 'もしわ' and new_new_words[-1] == 'で':
                        new_new_words[-1] += 'も'
                        new_new_words.append('しわ')
                        continue
                    elif new_new_words[-1] in combinations and w in combinations[new_new_words[-1]]:
                        new_new_words[-1] += w
                        continue
                #if i > 0 and tag in ['助動詞', '助詞', '接尾辞'] and words.postags[i-1] in ['動詞', '助動詞', '形容詞', '接尾辞', 'web誤脱']:
                #    new_words[-1] += w
                #    continue
                new_new_words.append(w)

            if len(new_new_words) == len(new_words):
                break
            new_words = new_new_words
            new_new_words = [] # second pass
        if ('て' in new_words or any(x in new_words for x in bad_characters) or any (x.endswith('っ') for x in new_words)) and file_name not in {'JA003_68.lab', 'JA012_3.lab', 'JA032_39.lab'}:
            print(file_name)
            print(original)
            print(words)
            print(new_words)
        with open(os.path.join(speaker_out_dir, file_name), 'w',encoding='utf8') as f:
            f.write(' '.join(new_words))
        word_set.update(new_words)

with open (os.path.join(resegmented_lab_dir, 'vocab.txt'), 'w', encoding='utf8') as f:
    for w, v in sorted(word_set.items(), key=lambda x: -x[1]):
        f.write(f"{w}\t{v}\n")
