import collections
import os

include_languages = {#'bulgarian',
    # 'german',
    #'french','portuguese',
    #'croatian',
                     #'swedish','tamil',
    # 'turkish',
            # 'ukrainian',
            # 'vietnamese',
            # 'swahili',
    #         'spanish', 'polish', 'czech',
     #'english',
     #'russian',
     #'hausa',
     #'arabic',
     'japanese',
    #'thai',
    #'mandarin',
                     }

root_dir = 'D:/Data/speech/model_training_corpora'

for lang in os.listdir(root_dir):
    if lang not in include_languages:
        continue
    print(lang)
    lang_dir = os.path.join(root_dir, lang)
    for corpus in os.listdir(lang_dir):
            if corpus.endswith('_temp'):
                continue
            #if 'common' not in corpus:
            #    continue
            corpus_dir = os.path.join(lang_dir, corpus)
            if not os.path.isdir(corpus_dir):
                continue
            print(corpus)
            speaker_info_path = os.path.join(corpus_dir, 'speaker_info.tsv')
            speakers = [x for x in os.listdir(corpus_dir) if os.path.isdir(os.path.join(corpus_dir, x))]

            if not os.path.exists(speaker_info_path):
                continue
            corpus_gender_counts = collections.Counter()
            corpus_gender_durations = collections.defaultdict(float)
            with open(speaker_info_path, 'r', encoding='utf8') as f:
                for line in f:
                    line = line.strip()
                    line = line.split('\t')
                    speaker = line[0]
                    if speaker not in speakers:
                        continue
                    try:
                        gender = line[2]
                    except IndexError:
                        gender = line[1]
                    corpus_gender_counts[gender] += 1
                    speaker_directory = os.path.join(corpus_dir, speaker)
                    if False:
                        for file in os.listdir(speaker_directory):
                            if file.endswith('.lab'):
                                continue
                            duration = librosa.get_duration(filename=os.path.join(speaker_directory, file))
                            corpus_gender_durations[gender] += duration
            print(corpus, corpus_gender_counts)

