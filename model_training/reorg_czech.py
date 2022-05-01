import collections
import os
import re
from bs4 import BeautifulSoup as bs
from praatio.utilities.constants import Interval
from praatio.textgrid import Textgrid, IntervalTier

corpus_root = r"D:\Data\speech\czech_corpora\czech_parliament"

word_set = collections.Counter()

bad_characters = {',', '.', ')'}

def utterance_cleanup(utterance: str):
    filtered = []
    for c in bad_characters:
        utterance = utterance.replace(c, '')
    for w in utterance.split():
        if w.startswith('+') or w.endswith('+') or w.startswith('=') or w.endswith('='):
            w = f"[{w}]"
        if '(' in w:
            w = w.split('(')[-1]
        filtered.append(w)
    word_set.update(filtered)
    return ' '.join(filtered)


for file in os.listdir(corpus_root):
    if not file.endswith('.trs'):
        continue
    with open(os.path.join(corpus_root, file), 'r', encoding='CP1250') as f:
        content = bs(f.read(), 'lxml')
    speaker_utterances = {}
    section = content.find('section')
    duration = float(section.get('endtime'))
    for turn in content.find_all(name='turn'):
        turn_begin = turn.get("starttime")
        speaker = turn.get("speaker")
        turn_end = turn.get("endtime")
        current_utterance = []
        current_begin = turn_begin
        unintelligible_section = None
        pronounce_section = None
        for line in turn.contents:
            if isinstance(line, str):
                line = line.strip()
                if line:
                    if unintelligible_section is not None:
                        unintelligible_section.append(line)
                    elif pronounce_section is None:
                        current_utterance.append(line)
                continue
            if line.name == 'event':
                if line.get("desc") in {"speaker", "noise"}:
                    continue
                if line.get("desc") == 'unintelligible':
                    if line.get("extent") == 'begin':
                        unintelligible_section = []
                    elif line.get('extent') == 'instantaneous':
                        current_utterance.append('[unintelligible]')
                    else:
                        print(line)
                        print(unintelligible_section)
                        current_utterance.append('[' + '_'.join(unintelligible_section).replace(' ', '_') + ']')
                        unintelligible_section = None
                elif line.get("type") == 'pronounce':
                    if line.get("extent") == 'begin':
                        pronounce_section = line.get('desc')
                    else:
                        current_utterance.append(pronounce_section)
                        pronounce_section = None
            elif line.name == 'sync':
                print(line)
                sync_time = float(line.get('time'))
                if current_utterance:
                    if speaker not in speaker_utterances:
                        speaker_utterances[speaker] = []
                    speaker_utterances[speaker].append(Interval(current_begin, sync_time, utterance_cleanup(' '.join(current_utterance))))
                current_begin = sync_time
                current_utterance = []

    tg = Textgrid(minTimestamp=0, maxTimestamp=duration)
    for speaker_id, intervals in speaker_utterances.items():
        tier = IntervalTier(speaker_id, intervals, minT=0, maxT=duration)
        tg.addTier(tier)
    tg.save(os.path.join(corpus_root, file.replace('.trs', '.TextGrid')), format='short_textgrid', includeBlankSpaces=True)
print(word_set)

with open(os.path.join(corpus_root, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
    for k, v in speaker_data.items():
        f.write(f"{k}\t{v}\n")