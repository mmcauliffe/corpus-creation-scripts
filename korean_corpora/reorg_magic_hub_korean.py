import collections
import os
import re
import shutil
import csv
import soundfile
from praatio.textgrid import openTextgrid, Textgrid, IntervalTier

root = r'D:\Data\speech\model_training_corpora\korean\Korean_Conversational_Speech_Corpus'


audio_dir = os.path.join(root, 'WAV')
audio_info = {}
for sound_file in os.listdir(audio_dir):
    if not sound_file.endswith('.wav'):
        continue
    sf = soundfile.info(os.path.join(audio_dir, sound_file))
    audio_info[sound_file.split('.')[0]] =  sf.duration
transcript_dir = os.path.join(root, 'TXT')

for text_file in os.listdir(transcript_dir):
    intervals = []
    root_name = text_file.split('.')[0]
    with open(os.path.join(transcript_dir, text_file), 'r', encoding='utf8') as inf:
        for line in inf:
            line = line.strip().split('\t')
            begin, end = line[0][1:-1].split(',')
            begin = float(begin)
            end = float(end)
            speaker = line[1]
            if speaker in ["0"]:
                continue
            transcript = line[-1]
            intervals.append([begin, end, transcript])
        tier = IntervalTier(speaker, intervals, minT=0.0, maxT=audio_info[root_name])
        tg = Textgrid(minTimestamp=0.0, maxTimestamp=audio_info[root_name])
        tg.addTier(tier)
        tg.save(os.path.join(audio_dir, root_name + '.TextGrid'), format='short_textgrid', includeBlankSpaces=True)

error

root = r'D:\Data\speech\model_training_corpora\korean\Korean_Scripted_Speech_Corpus_Daily_Use_Sentence'

audio_dir = os.path.join(root, 'WAV')

utt_file = os.path.join(root, 'UTTRANSINFO.txt')

with open(utt_file, 'r', encoding='utf8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for line in reader:
        print(line)
        speaker = line['SPEAKER_ID']
        file = line['UTTRANS_ID']
        transcript = line['TRANSCRIPTION']
        speaker_dir = os.path.join(root, speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        with open(os.path.join(speaker_dir, file.replace('.wav', '.lab')), 'w', encoding='utf8') as outf:
            outf.write(transcript)
        wavpath = os.path.join(audio_dir, speaker, file)
        if os.path.exists(wavpath):
            shutil.move(wavpath, os.path.join(speaker_dir, file))



