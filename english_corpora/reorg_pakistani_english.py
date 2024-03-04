import os
import shutil
import csv
from pathlib import Path
root_dir = Path(r'D:\Data\speech\model_training_corpora\english\Pakistani_English_Scripted_Speech_Corpus_Daily_Use_Sentence')

utterance_path = root_dir.joinpath('UTTERANCEINFO.txt')
texts = {}
utt2spk = {}
with open(utterance_path, encoding='utf8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for line in reader:
        texts[line['UTTRANS_ID']] = line['TRANSCRIPTION']
        utt2spk[line['UTTRANS_ID']] = line['SPEAKER_ID']
print(texts)
wav_dir = root_dir.joinpath('WAV')
for k,text in texts.items():
    speaker = utt2spk[k]
    wav_path = wav_dir.joinpath(speaker, k)
    speaker_dir = root_dir.joinpath(speaker)
    speaker_dir.mkdir(exist_ok=True)
    wav_path.rename(speaker_dir.joinpath(k))
    tf_path = speaker_dir.joinpath(k).with_suffix('.lab')
    with open(tf_path, 'w', encoding='utf8') as f:
        f.write(text)
