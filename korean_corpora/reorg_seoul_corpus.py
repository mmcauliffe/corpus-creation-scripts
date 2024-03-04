import collections
import os
import re
import shutil
import subprocess
from praatio.textgrid import openTextgrid, Textgrid, IntervalTier

korean_root = r'D:\Data\speech\benchmark_datasets'

seoul_corpus = os.path.join(korean_root, 'seoul_corpus')
original_textgrids = os.path.join(seoul_corpus, 'original')
training_textgrids = os.path.join(seoul_corpus, 'seoul_corpus_benchmark')
reference_dir = os.path.join(seoul_corpus, 'seoul_reference_alignments')

bad_chars = {}

speaker_info = {}

def fix_sample_rate():

    for speaker in os.listdir(training_textgrids):
        speaker_dir = os.path.join(training_textgrids, speaker)
        if not os.path.isdir(speaker_dir):
            continue
        for file in os.listdir(speaker_dir):
            if 'resampled' in file:
                os.remove(file)
            if file.endswith('.flac') and 'resampled' not in file:
                path = os.path.join(speaker_dir, file)
                resampled_file = path.replace('.flac', '_resampled.flac')
                subprocess.check_call(['sox', path, '-r', '16000', resampled_file])
                os.remove(path)
                os.rename(resampled_file, path)

def fix_textgrids():

    for file in os.listdir(original_textgrids):
        if os.path.isdir(os.path.join(original_textgrids, file)):
            continue
        speaker = file[:3]
        speaker_gender = file[3]
        speaker_age = file[4:6]
        print(speaker, speaker_gender, speaker_age)
        speaker_info[speaker] = {'gender': speaker_gender, 'age': speaker_age}
        speaker_directory = os.path.join(training_textgrids, speaker)
        reference_speaker_directory = os.path.join(reference_dir, speaker)
        os.makedirs(speaker_directory, exist_ok=True)
        os.makedirs(reference_speaker_directory, exist_ok=True)
        if not file.endswith('.TextGrid'):
            shutil.move(os.path.join(original_textgrids, file), os.path.join(speaker_directory, file))
            continue
        tg_path = os.path.join(original_textgrids, file)
        tg = openTextgrid(tg_path, includeEmptyIntervals=False, duplicateNamesMode='rename')
        orth = tg._tierDict['utt.prono.']
        new_intervals = []
        new_tg_path = os.path.join(speaker_directory, file)
        reference_tg_path = os.path.join(reference_speaker_directory, file)
        new_tg = Textgrid(minTimestamp=tg.minTimestamp, maxTimestamp=tg.maxTimestamp)
        for interval in orth._entries:
            if interval.label in {'<IVER>', '<SIL>', '<VOCNOISE>', '<NOISE>'}:
                continue
            text = interval.label.replace('<VOCNOISE>', '')
            if not text:
                continue
            if text[0] != '<' and text[-1] != '>':
                pass
                #text = ' '.join(hangul_jamo.compose(hangul_jamo.decompose(x)) for x in mecab.morphs(text) if x not in bad_chars)
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
        for interval in tg._tierDict['phoneme']._entries:
            if interval.label in {'<IVER>', '<SIL>', '<VOCNOISE>', '<NOISE>'}:
                continue
            text = interval.label
            if text.startswith('<'):
                text = 'spn'
            phone_intervals.append((interval.start, interval.end, text))
        word_intervals = []
        for interval in tg._tierDict['pWord.prono.']._entries:
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

if __name__ == '__main__':
    #fix_sample_rate()
    fix_textgrids()
