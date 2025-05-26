import re

import os
import soundfile
from praatio.utilities.constants import Interval
from praatio.textgrid import Textgrid, IntervalTier

root_dir = r"D:\Data\speech\model_training_corpora\spanish\mtedx_es\es-es/data"
output_dir = r"D:\Data\speech\model_training_corpora\spanish\mtedx_es"

bad_segments = {'IJrt_YsfK4Q_0000', 'IJrt_YsfK4Q_0001'}

for p in ['test', 'train', 'valid']:
    audio_dir = os.path.join(root_dir, p, 'wav')
    if os.path.exists(audio_dir):
        for file in os.listdir(audio_dir):
            if not os.path.exists(os.path.join(output_dir, file)):
                os.rename(os.path.join(audio_dir, file), os.path.join(output_dir, file))
    segments_file = os.path.join(root_dir, p, 'txt', 'segments')
    transcript_file = os.path.join(root_dir, p, 'txt', f'{p}.es')
    transcripts = []
    with open(transcript_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            transcripts.append(line)
    intervals = {}
    with open(segments_file, 'r', encoding='utf8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            segment_id, file, begin, end = line.split()
            if file not in intervals:
                intervals[file] = []
            begin, end = float(begin), float(end)
            if re.match(r'^[([<{].*[)}>\]]$', transcripts[i]):
                continue
            m = re.search(r'[([<{].*[)}>\]]', transcripts[i])
            if m and m.end() - m.start() / len(transcripts[i]) >= 0.5:
                continue
            if not re.match(r'^[([<{].*$', transcripts[i]):
                begin = float(begin) - 0.25
            if not re.match(r'.*[)}>\]]$', transcripts[i]):
                end = float(end) + 0.25
            if intervals[file] and begin < intervals[file][-1].end:
                if end - intervals[file][-1].start < 30:
                    intervals[file][-1] = Interval(intervals[file][-1].start, end, intervals[file][-1].label + " "+ transcripts[i])
                    continue
                begin = (begin + intervals[file][-1].end)/2
                print(file)
                print(intervals[file][-1].start, begin)
                print(begin, end)
                intervals[file][-1] = Interval(intervals[file][-1].start, begin,
                                               intervals[file][-1].label)
            if segment_id in bad_segments:
                continue
            intervals[file].append(Interval(begin, end, transcripts[i]))
    for file, interval_list in intervals.items():
        wav_path = os.path.join(output_dir, f'{file}.flac')
        tg_path = os.path.join(output_dir, f'{file}.TextGrid')
        info = soundfile.info(wav_path)
        duration = info.duration
        tg = Textgrid(minTimestamp=0, maxTimestamp=duration)
        interval_tier = IntervalTier(file, sorted(interval_list), minT=0, maxT=duration)
        tg.addTier(interval_tier)
        tg.save(tg_path, "short_textgrid", True)
