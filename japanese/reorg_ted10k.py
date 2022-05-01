import os
import re

import nagisa
import soundfile
from praatio.utilities.constants import Interval
from praatio.textgrid import Textgrid, IntervalTier

japanese_root = r'/mnt/d/Data/speech/japanese_corpora/tedxjp_10k'

audio_dir = os.path.join(japanese_root, 'wav')

segments_path = os.path.join(japanese_root, 'segments')
text_path = os.path.join(japanese_root, 'text')
utt2spk_path = os.path.join(japanese_root, 'utt2spk')

tsu_numbers = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十'}
bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';','〈', '〉', '-', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}


utt2spk={}
with open(utt2spk_path, 'r',  encoding='utf8') as f:
    for line in  f:
        line = line.strip()
        line = line.split()
        utt2spk[line[0]] = line[1]

texts={}
with open(text_path, 'r',  encoding='utf8') as f:
    for line in  f:
        line = line.strip()
        line = line.split()
        text = line[1]
        words = nagisa.tagging(text)
        new_words = []
        for i, w in enumerate(words.words):
            if len(new_words) and (new_words[-1].startswith('<') and not new_words[-1].endswith('>')):
                new_words[-1] += w
                continue
            elif len(new_words) and new_words[-1].endswith('っ'):
                w = 'っ' + w
                new_words[-1] = new_words[-1][:-1]
            elif len(new_words) and w == 'つ' and new_words[-1] in tsu_numbers:
                new_words[-1] += w
                continue
            if w in bad_chars:
                continue
            new_words.append(w)
        texts[line[0]] = ' '.join(new_words)

file_segments = {}
with open(segments_path, 'r',  encoding='utf8') as f:
    for line in  f:
        line = line.strip()
        utt, file, begin, end = line.split()
        if file not  in file_segments:
            file_segments[file] = []
        file_segments[file].append((utt, float(begin), float(end)))

for file, file_data in file_segments.items():
    wav_path = os.path.join(audio_dir, file+'.16k.wav')
    duration = soundfile.info(wav_path).duration
    tg = Textgrid(minTimestamp=0, maxTimestamp=duration)
    tiers = {}
    for utt, begin,  end in file_data:
        spk = utt2spk[utt]
        if spk not in tiers:
            tiers[spk] = []
        print(file, utt, begin, end, texts[utt])
        if tiers[spk] and tiers[spk][-1].end > begin:
            print(tiers[spk][-1], begin)
            mid_point = round((begin + tiers[spk][-1].end) / 2, 2)
            print(mid_point)
            tiers[spk][-1] = Interval(tiers[spk][-1].start, mid_point, tiers[spk][-1].label)
            begin = mid_point
        tiers[spk].append(Interval(begin, end, texts[utt]))
    for speaker_id, intervals in tiers.items():
        tier = IntervalTier(speaker_id, intervals, minT=0, maxT=duration)
        tg.addTier(tier)

    tg.save(os.path.join(japanese_root, file + '.TextGrid'), format='short_textgrid', includeBlankSpaces=True)
    os.rename(wav_path, os.path.join(japanese_root, file + '.wav'))