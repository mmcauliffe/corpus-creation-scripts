import os
import re
import shutil
from dataclasses import dataclass

import soundfile
from praatio import textgrid as tgio

from praatio.utilities.constants import Interval
in_dir = r"D:\Data\speech\Buckeye\mm_version"
aligned_dir = r"D:\Data\speech\Buckeye\reference"
benchmark_dir = r"D:\Data\speech\Buckeye\benchmark"

speakers = os.listdir(in_dir)

words = {}

word_line_pattern = re.compile(r"^(?P<time>[0-9.]+)  ?12[123] (?P<label>[-'_\w<>}{ ?=]+);?.*$")
phone_line_pattern = re.compile(r"^(?P<time>[0-9.]+)  ?12[123] (?P<label>[-'_\w<>}{ ?=]+)(\+1n?)?( ?;.*)?$")

typo_mapping = {
    'ynkow': 'yknow',
    'ynknow': 'yknow',
    'aderal': 'adderall',
    'femalee': 'female',
    'thier': 'their',
    'cheetohs': 'cheetos',
    'commerical': 'commercial',
    'diagnosises': 'diagnoses',
    'dieing': 'dying',
    'forgone': 'foregone',
    'hostle': 'hostel',
    'sevices': 'services',
    'varisty': 'varsity',
    "dont": "don't",
    "thats": "that's",
    "whats": "what's",
}

def load_file(path, max_time):
    begin = 0
    data = []
    if path.endswith('.words'):
        line_pattern = word_line_pattern
        line_type = 'words'
    else:
        line_pattern = phone_line_pattern
        line_type = 'phones'
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            m = line_pattern.match(line)
            if not m:
                if ('122' in line or '123' in line) and 'color' not in line:
                    print("NOMATCH", line)
                    print(line_type, repr(line))
                continue
            end = float(m.group("time"))
            if end > max_time:
                continue
            label = m.group("label")
            label = label.replace(" ", "_")
            if '<NOISE-' in label.upper() and '_' not in label:
                label = label.replace('<NOISE-', '')[:-1]
            elif '<NOSIE-' in label.upper() and '_' not in label:
                label = label.replace('<NOSIE-', '')[:-1]
            elif '<LAUH-' in label.upper() and '_' not in label:
                label = label.replace('<LAUH-', '')[:-1]
            elif '<VOCNOISE-' in label.upper() and '_' not in label:
                label = label.replace('<VOCNOISE-', '')[:-1]
            elif '<EXT-' in label.upper() and '_' not in label:
                label = label.replace('<EXT-', '')[:-1]
            elif label.upper().startswith('<CUTOFF'):
                label = "<CUTOFF>"
            elif label.upper().startswith('<HES'):
                label = '<HES>'
            elif label.upper().startswith('<IVER'):
                label = ''
            elif 'IVER' in label.upper():
                label = ''
            elif label.startswith('{'):
                label = ''
            elif label.upper().startswith('<LAUGH-') and '_' not in label:
                label = label.replace('<LAUGH-', '')[:-1]
            elif label.upper().startswith('<LAUGH-'):
                label = '<LAUGH>'
            elif label.upper().startswith('<EXCLUDE-'):
                label = '<EXCLUDE>'
            elif label.upper().startswith('<UNKNOWN'):
                label = '<UNKNOWN>'
            elif label.upper().startswith('<ERROR'):
                label = '<ERROR>'
            elif label.upper() == 'UNKNOWN':
                label = 'spn'
            elif label.lower() == '<laughyet>':
                label = 'yet'
            elif label.lower() == '<noisethere>':
                label = 'there'
            elif label.lower() == '<thirty>':
                label = ''
            elif label.upper() in ['<VOCNOISE>', '<VOCNOISED>', 'VOCNOISE',
                           '<SIL>', 'SIL',
                           '<NOISE>', 'NOISE',
                           '<LAUGH>', 'LAUGH',
                           '<IVER>', 'IVER',
                           ]:
                label = ''
            if '=' in label:
                label = '<UNKNOWN>'
            elif '_' in label:
                label = '<UNKNOWN>'
            elif label.endswith('-'):
                label = '<UNKNOWN>'
            if label.endswith("s'"):
                label += 's'
            for typo, real_word in typo_mapping.items():
                if label == typo:
                    label = real_word
                    break
            if label:
                data.append(Interval(begin, end, label))
            begin = end
    data[-1] = Interval(data[-1].start, max_time, data[-1].label)
    return data

def construct_phrases(word_intervals, max_time):
    data = []
    cur_utt = []
    for i, w in enumerate(word_intervals):
        if cur_utt and i != 0:
            if w.start - word_intervals[i-1].end > 0.15:
                begin = cur_utt[0].start - 0.025
                if begin < 0:
                    begin = 0
                end = cur_utt[-1].end + 0.025
                if end > max_time:
                    end = max_time
                label = ' '.join(x.label for x in cur_utt)
                data.append(Interval(begin, end, label))
                cur_utt = []
        cur_utt.append(w)
    return data

for speaker in speakers:
    #if speaker != 's23':
    #    continue
    speaker_dir = os.path.join(in_dir, speaker)
    files = {}
    durations = {}
    bench_out_dir = os.path.join(benchmark_dir, speaker)
    os.makedirs(bench_out_dir, exist_ok=True)
    for f in os.listdir(speaker_dir):
        file_name = os.path.splitext(f)[0]
        if f.endswith('.wav'):
            durations[file_name] = soundfile.info(os.path.join(speaker_dir, f)).duration
            sound_path = os.path.join(bench_out_dir, f)
            if not os.path.exists(sound_path):
                shutil.copyfile(os.path.join(speaker_dir, f), sound_path)

    for f in sorted(os.listdir(speaker_dir)):
        file_name = os.path.splitext(f)[0]

        if f.endswith('.words'):
            intervals = load_file(os.path.join(speaker_dir, f), durations[file_name])
            file_type = 'words'
        elif f.endswith('.phones'):
            intervals = load_file(os.path.join(speaker_dir, f), durations[file_name])
            file_type = 'phones'
        else:
            continue
        if file_name not in files:
            files[file_name] = {'words': [], 'phones': []}
        files[file_name][file_type].extend(intervals)

    out_dir = os.path.join(aligned_dir, speaker)
    os.makedirs(out_dir, exist_ok=True)
    bench_out_dir = os.path.join(benchmark_dir, speaker)
    os.makedirs(bench_out_dir, exist_ok=True)
    for file_name in files:
        print(file_name)
        utterances = construct_phrases(files[file_name]['words'], durations[file_name])

        output_path = os.path.join(bench_out_dir, f"{file_name}.TextGrid")
        tg = tgio.Textgrid(maxTimestamp=durations[file_name])
        tier = tgio.IntervalTier(speaker, utterances, minT=0, maxT=durations[file_name])

        tg.addTier(tier)
        tg.save(output_path, includeBlankSpaces=True, format="long_textgrid", reportingMode="error")

        output_path = os.path.join(out_dir, f"{file_name}.TextGrid")
        tg = tgio.Textgrid(maxTimestamp=durations[file_name])
        word_tier = tgio.IntervalTier("words", files[file_name]["words"], minT=0, maxT=durations[file_name])
        phone_tier = tgio.IntervalTier("phones", files[file_name]["phones"], minT=0, maxT=durations[file_name])
        tg.addTier(word_tier)
        tg.addTier(phone_tier)

        tg.save(output_path, includeBlankSpaces=True, format="long_textgrid", reportingMode="error")