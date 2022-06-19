import os
import csv
import shutil
import re
import sys
from collections import Counter
ignore = []
try:
    import nagisa
except ImportError:
    ignore.append('japanese')
try:
    import hanziconv
    import spacy_pkuseg

    seg = spacy_pkuseg.pkuseg(model_name='/mnt/c/Users/michael/Documents/Dev/Tools/3p_models/pkuseg/mixed')
except ImportError as e:
    print('IGNORING MANDARIN SEGMENTATION due to',e)
    ignore.extend(['mandarin_china', 'mandarin_taiwan'])
try:
    sys.path.insert(0, '/mnt/c/Users/michael/Documents/Dev/thai-word-segmentation')
    from thainlplib import ThaiWordSegmentLabeller
    import tensorflow as tf
except ImportError as e:
    print('IGNORING THAI SEGMENTATION due to',e)
    ignore.append('thai')


saved_model_path='/mnt/c/Users/michael/Documents/Dev/thai-word-segmentation/saved_model'

def nonzero(a):
    return [i for i, e in enumerate(a) if e != 0]

def split(s, indices):
    return [s[i:j] for i,j in zip(indices, indices[1:]+[None])]

languages = [
    'bulgarian',
    # 'german',
    #'french','portuguese',
    'serbian', #'swedish','tamil',
     'turkish',
             'ukrainian',
             'vietnamese',
             'swahili',
    #         'spanish', 'polish', 'czech',
     #'english',
     'russian',
     'hausa',
     #'arabic',
     'japanese',
    'thai',
    'mandarin_china',
    'mandarin_taiwan'
]
root_directory = r'/mnt/d/data/speech/CommonVoice'


partitions = ['validated', 'other']


bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';', '<', '〈', '〉', '-', '>', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}

for lang in languages:
    if lang in ignore:
        print("IGNORING", lang)
        continue
    lang_dir = os.path.join(root_directory, 'common_voice_{}'.format(lang))
    clip_dir = os.path.join(lang_dir, 'clips')
    clip_info = {}
    speaker_counts = Counter()
    count = 0
    speaker_information = {}
    bad_files = set()
    bad_sentences = set()
    with open(os.path.join(lang_dir, 'invalidated.tsv'), 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for line in reader:
            bad_files.add(line['path'])
    with open(os.path.join(lang_dir, 'reported.tsv'), 'r', encoding='utf8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for line in reader:
            bad_sentences.add(line['sentence'])
    if lang == 'thai':
        session = tf.Session()
        model = tf.saved_model.loader.load(session, [tf.saved_model.tag_constants.SERVING], saved_model_path)
        signature = model.signature_def[tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
        graph = tf.get_default_graph()

        g_inputs = graph.get_tensor_by_name(signature.inputs['inputs'].name)
        g_lengths = graph.get_tensor_by_name(signature.inputs['lengths'].name)
        g_training = graph.get_tensor_by_name(signature.inputs['training'].name)
        g_outputs = graph.get_tensor_by_name(signature.outputs['outputs'].name)
    language_partitions = partitions
    if lang in {'swahili', 'tamil'}:
        language_partitions += ['other']
    for p in language_partitions:
        path = os.path.join(lang_dir, p + '.tsv')
        with open(path, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f, delimiter='\t', quotechar='"')
            for line in reader:
                speaker = line['client_id']
                path = line['path']
                text = line['sentence']
                if path in bad_files or text in bad_sentences:
                    mp3_path = os.path.join(lang_dir, speaker, path)
                    if os.path.exists(mp3_path):
                        os.remove(mp3_path)
                    if os.path.exists(mp3_path.replace('.mp3', '.lab')):
                        os.remove(mp3_path.replace('.mp3', '.lab'))
                    continue
                if text in bad_sentences:
                    continue
                if speaker not in speaker_information:
                    speaker_information[speaker] = {
                        'age': line['age'],
                        'gender': line['gender'],
                        'accents': line['accents'],
                        'locale': line['locale'],
                    }
                if path not in clip_info and not os.path.exists(os.path.join(lang_dir, speaker, path)):
                    if lang == 'japanese':
                        words = nagisa.tagging(text)
                        new_words = []
                        for i, w in enumerate(words.words):
                            if len(new_words) and (new_words[-1].startswith('<') and not new_words[-1].endswith('>')):
                                new_words[-1] += w
                                continue
                            elif '<' in w and not w.startswith('<'):
                                x = w.split('<')
                                new_words.append(x[0])
                                new_words.append('<'+ x[1])
                                continue
                            elif len(new_words) and new_words[-1].endswith('っ'):
                                w = 'っ' + w
                                new_words[-1] = new_words[-1][:-1]
                            if w in bad_chars:
                                continue
                            new_words.append(w)
                        print(text)
                        print(new_words)
                        text = ' '.join(new_words)
                    elif lang == 'german':
                        text = text.replace('ß', 'ss')
                    elif lang == 'thai':
                        inputs = [ThaiWordSegmentLabeller.get_input_labels(text)]
                        lengths = [len(text)]
                        y = session.run(g_outputs, feed_dict={g_inputs: inputs, g_lengths: lengths, g_training: False})
                        #print(text)
                        new_words = []
                        for w in split(text, nonzero(y)):
                            #print(w)
                            w = w.replace(',', '')
                            w = re.sub(r'\.', '. ', w)
                            w = w.strip()
                            if not w:
                                continue
                            if new_words and w == '.':
                                new_words[-1] += w
                                continue
                            if w.endswith(' '):
                                w = w[:-1]
                            new_words.append(w)
                            text = ' '.join(new_words).replace(' . ', '. ')
                    elif lang == 'mandarin_china':

                        words = [hanziconv.HanziConv.toSimplified(x) for x in seg.cut(text) if x not in bad_chars]
                        print(text)
                        print(words)
                        text = ' '.join(words)
                    elif lang == 'mandarin_taiwan':
                        words = [hanziconv.HanziConv.toTraditional(x) for x in seg.cut(text) if x not in bad_chars]
                        print(text)
                        print(words)
                        text = ' '.join(words)
                    clip_info[line['path']] = {'speaker': line['client_id'], 'text': text}
                    speaker_counts[line['client_id']] += 1
                    count += 1
                else:
                    continue
                    if clip_info[line['path']]['speaker'] != line['client_id'] or clip_info[line['path']]['text'] != line['sentence']:
                        print(clip_info[line['path']])
                        print(line)
                        error
    if lang == 'thai':
        session.close()
    for k,v in speaker_counts.items():
        print(k, v)

    print(len(speaker_counts))
    print(count)
    print(len(clip_info))

    with open(os.path.join(lang_dir, 'speaker_info.tsv'), 'w', encoding='utf8') as f:
        for speaker, info in speaker_information.items():
            f.write(f'{speaker}\t{info["age"]}\t{info["gender"]}\t{info["accents"]}\t{info["locale"]}\n')

    for k, v in clip_info.items():
        speaker = v['speaker']
        out_dir = os.path.join(lang_dir, speaker)
        os.makedirs(out_dir, exist_ok=True)
        text = v['text']
        mp3_path = k
        lab_path = k.replace('.mp3', '.lab')
        if os.path.exists(os.path.join(out_dir, lab_path)):
            continue
        if os.path.exists(clip_dir) and os.path.exists(os.path.join(clip_dir, mp3_path)):
            os.rename(os.path.join(clip_dir, mp3_path), os.path.join(out_dir, mp3_path))
        with open(os.path.join(out_dir, lab_path), 'w', encoding='utf8') as f:
            f.write(text)