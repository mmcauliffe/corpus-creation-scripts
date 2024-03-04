import collections
import os
from konlpy.tag import Kkma
from konlpy.tag import Mecab
import hangul_jamo

mecab = Mecab('/home/michael/miniconda3/envs/koreanseg/lib/mecab/dic/mecab-ko-dic')

korean_root = '/mnt/d/Data/speech/GlobalPhone/korean'
trl_dir = os.path.join(korean_root, 'trl')
lab_dir = os.path.join(korean_root, 'lab')

word_set = collections.Counter()

bad_chars = {}

if __name__ == '__main__':
    for file in os.listdir(trl_dir):
        speaker_id = os.path.splitext(file)[0]
        path = os.path.join(trl_dir, file)
        output_dir = os.path.join(lab_dir, speaker_id[2:])
        os.makedirs(output_dir, exist_ok=True)
        texts = {}
        current_utterance = 0
        print(file)
        with open(path, 'r', encoding='korean') as f:
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
                    words = [hangul_jamo.compose(hangul_jamo.decompose(x)) for x in mecab.morphs(line) if x not in bad_chars]
                    #print(line)
                    #print(text)
                    #print(' '.join(words))
                    word_set.update(words)
                    if current_utterance not in texts:
                        texts[current_utterance] = words
                    else:
                        texts[current_utterance] += words

        for utterance, words in texts.items():
            path = os.path.join(output_dir, f'{speaker_id}_{utterance}.lab')
            with open(path, 'w', encoding='utf8') as f:
                f.write(' '.join(words))
