import os
import re
import shutil
from dataclasses import dataclass

import soundfile
from praatio import textgrid as tgio

from praatio.utilities.constants import Interval
in_dir = r"D:\Data\speech\benchmark_datasets\timit"
aligned_dir = r"D:\Data\speech\benchmark_datasets\timit\reference"
benchmark_dir = r"D:\Data\speech\benchmark_datasets\timit\benchmark"

utt2spk = {}
phone_data = {}
word_data = {}
regions = os.listdir(in_dir)
durations = {}

affricated_dh_count = 0
total_dh_count = 0

for region in regions:
    if not region.startswith('DR'):
        continue
    speakers = os.listdir(os.path.join(in_dir, region))
    for s in speakers:
        speaker = f"{region}_{s}"
        orig_speaker_dir = os.path.join(in_dir, region, s)
        if not os.path.isdir(orig_speaker_dir):
            continue
        output_speaker_dir = os.path.join(benchmark_dir, speaker)
        os.makedirs(output_speaker_dir, exist_ok=True)
        for file in os.listdir(output_speaker_dir):
            if file.lower().endswith('.wav'):
                utterance = file.split('.')[0]
                durations[utterance] = soundfile.info(os.path.join(output_speaker_dir, file)).duration
        for file in os.listdir(orig_speaker_dir):
            if file.lower().endswith('.wav'):
                file_name = file.split('.')[0]
                utterance = f"{speaker}_{file_name}"
                durations[utterance] = soundfile.info(os.path.join(orig_speaker_dir, file)).duration
                os.rename(os.path.join(orig_speaker_dir, file),
                          os.path.join(output_speaker_dir, f"{speaker}_{file_name}.wav"))
            elif file.lower().endswith('.txt'):
                file_name = file.split('.')[0]
                with open(os.path.join(orig_speaker_dir, file)) as f:
                    text = f.read().strip()
                    text =text.split(maxsplit=2)[-1]
                with open(os.path.join(output_speaker_dir, f"{speaker}_{file_name}.lab"), 'w', encoding='utf8') as f:
                    f.write(text)
            elif file.lower().endswith('.phn'):
                file_name = file.split('.')[0]
                utterance = f"{speaker}_{file_name}"
                utt2spk[utterance] = speaker
                phones = []
                with open(os.path.join(orig_speaker_dir, file)) as f:
                    for line in f:
                        line=line.strip()
                        begin, end, phone =line.split(maxsplit=2)
                        if phone in {'h#', 'pau', 'epi'}:
                            continue
                        begin = int(begin)/16000
                        end = int(end)/16000
                        if phone in {'d', 'k', 'g','p', 'b', 't'} and phones and phones[-1][-1] == phone + 'cl':
                            phones[-1][-1] = phone
                            phones[-1][1] = end
                            continue
                        elif phone in {'ch'} and phones and phones[-1][-1] == 'tcl':
                            phones[-1][-1] = phone
                            phones[-1][1] = end
                            continue
                        elif phone in {'jh'} and phones and phones[-1][-1] == 'dcl':
                            phones[-1][-1] = phone
                            phones[-1][1] = end
                            continue
                        elif phone == 'dh' and phones and phones[-1][-1] == 'dcl':
                            affricated_dh_count += 1
                        if phone == 'dh':
                            total_dh_count +=1
                        phones.append([begin, end,phone])
                phone_data[utterance] = phones
            elif file.lower().endswith('.wrd'):
                file_name = file.split('.')[0]
                utterance = f"{speaker}_{file_name}"
                words = []
                with open(os.path.join(orig_speaker_dir, file)) as f:
                    for line in f:
                        line=line.strip()
                        begin, end, word =line.split(maxsplit=2)
                        begin = int(begin)/16000
                        end = int(end)/16000
                        if words and words[-1][1] > begin:
                            begin = words[-1][1]
                        if begin == end:
                            continue
                        words.append([begin, end,word])
                word_data[utterance] = words

print("dh affricates", affricated_dh_count, total_dh_count)
error
for utterance, speaker in utt2spk.items():
    print(utterance)
    phones = phone_data[utterance]
    words = word_data[utterance]
    print(words)
    print(phones)
    duration = durations[utterance]
    output_dir = os.path.join(aligned_dir, speaker)
    os.makedirs(output_dir,exist_ok=True)
    tg = tgio.Textgrid(maxTimestamp=duration)
    word_tier = tgio.IntervalTier("words", [Interval(*x) for x in words], minT=0, maxT=duration)
    phone_tier = tgio.IntervalTier("phones", [Interval(*x) for x in phones], minT=0, maxT=duration)
    tg.addTier(word_tier)
    tg.addTier(phone_tier)

    tg.save(os.path.join(output_dir, utterance+'.TextGrid'),
            includeBlankSpaces=True, format="long_textgrid", reportingMode="error")
