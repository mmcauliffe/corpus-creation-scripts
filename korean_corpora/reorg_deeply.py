import os
import json

root = r"D:\Data\speech\korean_corpora"
from konlpy.tag import Kkma
from konlpy.tag import Mecab

mecab = Mecab('/home/michael/miniconda3/envs/reorg/lib/mecab/dic/mecab-ko-dic')

corpora = ["KoreanReadSpeechCorpus", #"Parent-ChildVocalInteraction"
           ]

for c in corpora:
    corpus_dir = os.path.join(root,c)
    with open(os.path.join(corpus_dir, 'info.json'), 'r', encoding='utf8') as f:
        data = json.load(f)
    for loc, loc_data in data.items():
        loc_dir = os.path.join(corpus_dir, 'sub1001')
        for file_name, file_data in loc_data.items():
            print(file_name)
            print(file_data)
            speaker = file_data['subjectID'] + file_data['speaker']
            text = file_data['text']
            speaker_dir = os.path.join(corpus_dir, speaker)
            os.makedirs(speaker_dir,exist_ok=True)
            wav_path = os.path.join(loc_dir,f'{file_name}.wav')
            if os.path.exists(wav_path):
                os.rename(wav_path, os.path.join(speaker_dir,f'{file_name}.wav'))
            with open(os.path.join(speaker_dir, f'{file_name}.lab'), 'w',encoding='utf8') as labf:
                labf.write(text)