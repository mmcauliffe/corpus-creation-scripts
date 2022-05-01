import collections
import os
import re
import shutil

import hangul_jamo
from praatio.textgrid import openTextgrid, Textgrid, IntervalTier
from konlpy.tag import Kkma
from konlpy.tag import Mecab

mecab = Mecab('/home/michael/miniconda3/envs/reorg/lib/mecab/dic/mecab-ko-dic')

korean_root = '/mnt/d/Data/speech/korean_corpora'

seoul_corpus = os.path.join(korean_root, 'seoul_corpus')
original_textgrids = os.path.join(seoul_corpus, 'original')
training_textgrids = os.path.join(seoul_corpus, 'seoul_corpus_benchmark')
reference_dir = os.path.join(seoul_corpus, 'seoul_reference_alignments')
zeroth_corpus = os.path.join(korean_root, 'zeroth_korean')

bad_chars = {}

speaker_info = {}

for file in os.listdir(original_textgrids):
    if os.path.isdir(os.path.join(original_textgrids, file)):
        continue
    speaker = file[:3]
    speaker_gender = file[3]
    speaker_age = file[4:6]
    print(speaker, speaker_gender, speaker_age)
    speaker_info[speaker] = {'gender': speaker_gender, 'age':speaker_age}
    speaker_directory = os.path.join(training_textgrids, speaker)
    reference_speaker_directory = os.path.join(reference_dir, speaker)
    os.makedirs(speaker_directory, exist_ok=True)
    os.makedirs(reference_speaker_directory, exist_ok=True)
    if not file.endswith('.TextGrid'):
        shutil.move(os.path.join(original_textgrids, file), os.path.join(speaker_directory, file))
        continue
    tg_path = os.path.join(original_textgrids, file)
    tg = openTextgrid(tg_path, includeEmptyIntervals=False, duplicateNamesMode='rename')
    orth = tg.tierDict['utt.prono.']
    new_intervals = []
    new_tg_path = os.path.join(speaker_directory, file)
    reference_tg_path = os.path.join(reference_speaker_directory, file)
    new_tg = Textgrid(minTimestamp=tg.minTimestamp, maxTimestamp=tg.maxTimestamp)
    for interval in orth.entryList:
        if interval.label in {'<IVER>', '<SIL>', '<VOCNOISE>', '<NOISE>'}:
            continue
        text = interval.label.replace('<VOCNOISE>', '')
        if not text:
            continue
        if text[0] != '<' and text[-1] != '>':
            text = ' '.join(hangul_jamo.compose(hangul_jamo.decompose(x)) for x in mecab.morphs(text) if x not in bad_chars)
        else:
            text = re.sub(r'\s','_', text)
        begin = max(interval.start - 0.25, 0)
        end = min(interval.end + 0.25, orth.maxTimestamp)
        if new_intervals and begin <= new_intervals[-1][1]:
            new_intervals[-1][1] = end
            new_intervals[-1][2] += ' ' + text
        else:
            new_intervals.append([begin, end, text])
    tier = IntervalTier(speaker, new_intervals,minT=tg.minTimestamp, maxT=tg.maxTimestamp)
    new_tg.addTier(tier)
    new_tg.save(new_tg_path,includeBlankSpaces=True, format='short_textgrid')
    reference_tg = Textgrid(minTimestamp=tg.minTimestamp, maxTimestamp=tg.maxTimestamp)
    phone_intervals = []
    for interval in tg.tierDict['phoneme'].entryList:
        if interval.label in {'<IVER>', '<SIL>', '<VOCNOISE>', '<NOISE>'}:
            continue
        text = interval.label
        if text.startswith('<'):
            text = 'spn'
        phone_intervals.append((interval.start, interval.end, text))
    word_intervals = []
    print(tg.tierNameList)
    for interval in tg.tierDict['pWord.prono.'].entryList:
        if interval.label in {'<IVER>', '<SIL>', '<VOCNOISE>', '<NOISE>'}:
            continue
        text = interval.label
        if text.startswith('<'):
            text = re.sub(r'\s','_', text)
        word_intervals.append((interval.start, interval.end, text))
    word_tier = IntervalTier('words', word_intervals, minT=tg.minTimestamp, maxT=tg.maxTimestamp)
    phone_tier = IntervalTier('phones', phone_intervals, minT=tg.minTimestamp, maxT=tg.maxTimestamp)
    reference_tg.addTier(word_tier)
    reference_tg.addTier(phone_tier)
    reference_tg.save(reference_tg_path, format='short_textgrid', includeBlankSpaces=True)

