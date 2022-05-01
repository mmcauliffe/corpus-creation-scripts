import os

training_root = '/mnt/d/Data/speech/model_training_corpora'


languages = ['bulgarian', 'french', 'german', 'portuguese', 'polish', 'turkish',
             'croatian', 'swedish', 'korean', 'thai', 'mandarin', 'tamil',
             'czech', 'japanese', 'vietnamese', 'ukrainian', 'swahili', 'spanish',
             'russian', 'hausa']


full_names = {
                'AR': 'arabic',
                'BG': 'bulgarian',
                'CH': 'mandarin',
                'WU': 'cantonese',
                'CR': 'croatian',
                'CZ': 'czech',
                'FR': 'french',
                'GE': 'german',
                'HA': 'hausa',
                'JA': 'japanese',
                'KO': 'korean',
                'RU': 'russian',
                'PO': 'portuguese',
                'PL': 'polish',
                'SP': 'spanish',
                'SA': 'swahili',
                'SW': 'swedish',
                'TA': 'tamil',
                'TH': 'thai',
                'TU': 'turkish',
                'VN': 'vietnamese',
                'UA': 'ukrainian'
                }


for lang_code, name in full_names.items():
    print(lang_code, name)
    lang_corpus_dir = os.path.join(training_root, name)
    globalphone_corpus_dir = os.path.join(lang_corpus_dir, f'globalphone_{lang_code.lower()}')
    print(globalphone_corpus_dir, os.path.exists(globalphone_corpus_dir))
    if not os.path.exists(globalphone_corpus_dir):
        globalphone_corpus_dir =os.path.join(lang_corpus_dir, f'globalphone_{name.lower()}')
        print(globalphone_corpus_dir, os.path.exists(globalphone_corpus_dir))
        if not os.path.exists(globalphone_corpus_dir):
            continue
    for speaker in os.listdir(globalphone_corpus_dir):
        speaker_dir = os.path.join(globalphone_corpus_dir, speaker)
        if not os.path.isdir(speaker_dir):
            continue
        if not speaker.startswith(lang_code):
            os.rename(speaker_dir,
                      os.path.join(globalphone_corpus_dir, lang_code+speaker))
