import collections
import os
from konlpy.tag import Kkma
from konlpy.tag import Mecab
import hangul_jamo
import num2words
import re
mecab = Mecab('/home/michael/miniconda3/envs/reorg/lib/mecab/dic/mecab-ko-dic')

root_dir = '/mnt/d/Data/speech/model_training_corpora/korean'
corpora = ['pansori_tedxkr']

bad_chars = {'!', '.', '~', '^^', ',', '~!!!', '?', ';;', '~~~', '~~', '??', '.^^', '~~^^*', '~!!', '”', '♪'}

replacements = {'13000km': '13000 킬로미터'}

for c in corpora:
    corpus_dir = os.path.join(root_dir, c)
    for speaker in os.listdir(corpus_dir):
        speaker_dir = os.path.join(corpus_dir, speaker)
        if not os.path.isdir(speaker_dir):
            continue
        print(speaker_dir)
        for dialog in os.listdir(speaker_dir):
            for file in os.listdir(os.path.join(speaker_dir, dialog)):
                if not file.endswith('.lab'):
                    continue
                file_path = os.path.join(speaker_dir, dialog, file)
                with open(file_path, 'r',encoding='utf8') as f:
                    text = f.read().strip()
                text = re.sub(r'(\d)~(\d)', r'\1 에서 \2', text)
                for k,v in replacements.items():
                    text = text.replace(k, v)
                words = [hangul_jamo.compose(hangul_jamo.decompose(x)) for x in mecab.morphs(text) if x not in bad_chars]
                new_words = []
                for w in words:
                    if re.search(r'\d', w):
                        num = num2words.num2words(int(w),lang='ko')
                        w = num
                    elif w == '+':
                        w = '플러스'
                    new_words.append(w)
                    if re.search(r'[^\w\s]', w):
                        print(w)
                        print(text)
                        error
                with open(file_path, 'w', encoding='utf8') as f:
                    f.write(' '.join(new_words))