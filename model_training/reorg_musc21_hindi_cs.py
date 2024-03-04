import os
from praatio.textgrid import Textgrid, IntervalTier
from praatio.utilities.constants import Interval
import soundfile
corpus_root = r'D:\Data\speech\hindi_corpora\musc2021_cs_hindi'

for split in ['test', 'train']:

    utt2spk = {}
    texts = {}
    segments = {}
    folder_path = os.path.join(corpus_root, split)
    transcripts_folder = os.path.join(folder_path, 'transcripts')
    with open(os.path.join(transcripts_folder, 'utt2spk'), 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utt_id, speaker = line.split()
            utt2spk[utt_id] = speaker
    with open(os.path.join(transcripts_folder, 'text'), 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utt_id, text = line.split(maxsplit=1)
            texts[utt_id] = text
    with open(os.path.join(transcripts_folder, 'segments'), 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utt_id, file, begin, end = line.split()
            if file not in segments:
                segments[file] = []
            segments[file].append({'begin': float(begin), "end": float(end), 'speaker': utt2spk[utt_id], 'text': texts[utt_id]})
    for f, seg_list in segments.items():
        wav_path = os.path.join(folder_path, f"{f}.wav")
        duration = soundfile.info(wav_path).duration
        tg = Textgrid(minTimestamp=0, maxTimestamp=duration)
        tiers = {}
        for seg in seg_list:
            if seg['speaker'] not in tiers:
                tiers[seg['speaker']] = IntervalTier(seg['speaker'], [], minT=0, maxT=duration)
            tiers[seg['speaker']].entryList.append(Interval(seg['begin'], seg['end'], seg['text']))
        for t in tiers.values():
            tg.addTier(t)
        tg.save(os.path.join(folder_path, f"{f}.TextGrid"), 'short_textgrid', includeBlankSpaces = True)
