import os
import re
import yaml
gp_dir = '/media/share/corpora/GlobalPhone'

dictionary_root_dirs = ['/data/mmcauliffe/mfa_output/models', '/data/mmcauliffe/mfa_output/2.0_archived']

for dictionary_root_dir in dictionary_root_dirs:
    speaker_dialects = {}

    lang_encodings = {
                    'Arabic': 'iso-8859-1',
                    'Bulgarian': 'utf8',
                    'Mandarin': 'gb2312',
                    #'Wu': 'gb2312',
                    'Croatian': 'iso-8859-2',
                    'Czech': 'iso-8859-2',
                    'French': 'iso-8859-1',
                    'German': 'iso-8859-1',
                    'Hausa': 'iso-8859-1',
                    'Japanese': 'eucjp',
                    'Korean': 'korean',
                    'Russian': 'koi8-r',
                    'Portuguese': 'iso-8859-1',
                    'Polish': 'utf8',
                    'Spanish': 'iso-8859-1',
                    'Swedish': 'iso-8859-1',
                    'Swahili': 'utf8',
                    'Tamil': 'utf8',
                    'Thai': 'utf8',
                    'Turkish': 'iso-8859-9',
                    'Vietnamese': 'utf8',
                    'Ukrainian': 'utf8',
                    }

    dialect_dictionary_mapping = {
        'Northern Vietnam': os.path.join(dictionary_root_dir, 'vietnamese_hanoi_mfa.dict'),
        'Southern Vietnam': os.path.join(dictionary_root_dir, 'vietnamese_ho_chi_minh_city_mfa.dict'),
        'Castellano': os.path.join(dictionary_root_dir, 'spanish_spain_mfa.dict'),
        'Beijing': os.path.join(dictionary_root_dir, 'mandarin_erhua_mfa.dict'),
    }

    language_dictionary_mapping = {
        'Arabic': os.path.join(dictionary_root_dir, 'bulgarian_mfa.dict'),
        'Bulgarian': os.path.join(dictionary_root_dir, 'bulgarian_mfa.dict'),
        'Croatian': os.path.join(dictionary_root_dir, 'croatian_mfa.dict'),
        'Czech': os.path.join(dictionary_root_dir, 'czech_mfa.dict'),
        'French': os.path.join(dictionary_root_dir, 'french_mfa.dict'),
        'German': os.path.join(dictionary_root_dir, 'german_mfa.dict'),
        'Hausa': os.path.join(dictionary_root_dir, 'hausa_mfa.dict'),
        'Japanese': os.path.join(dictionary_root_dir, 'japanese_mfa.dict'),
        'Korean': os.path.join(dictionary_root_dir, 'korean_mfa.dict'),
        'Mandarin': os.path.join(dictionary_root_dir, 'mandarin_china_mfa.dict'),
        'Polish': os.path.join(dictionary_root_dir, 'polish_mfa.dict'),
        'Portuguese': os.path.join(dictionary_root_dir, 'portuguese_brazil_mfa.dict'),
        'Russian': os.path.join(dictionary_root_dir, 'russian_mfa.dict'),
        'Spanish': os.path.join(dictionary_root_dir, 'spanish_latin_america_mfa.dict'),
        'Swahili': os.path.join(dictionary_root_dir, 'swahili_mfa.dict'),
        'Swedish': os.path.join(dictionary_root_dir, 'swedish_mfa.dict'),
        'Tamil': os.path.join(dictionary_root_dir, 'tamil_mfa.dict'),
        'Thai': os.path.join(dictionary_root_dir, 'thai_mfa.dict'),
        'Turkish': os.path.join(dictionary_root_dir, 'turkish_mfa.dict'),
        'Ukrainian': os.path.join(dictionary_root_dir, 'ukrainian_mfa.dict'),
        'Vietnamese': os.path.join(dictionary_root_dir, 'vietnamese_hue_mfa.dict'),
        #'Wu': os.path.join(dictionary_root_dir, 'wu_mfa.dict'),
    }


    all_speaker_dictionaries = {}

    for lang in language_dictionary_mapping.keys():
        #if lang != 'Arabic':
        #    continue
        print(lang)
        speaker_info_dir = os.path.join(gp_dir, lang, lang, 'spk')
        if not os.path.exists(speaker_info_dir):
            continue
        speaker_dictionaries = {}
        speaker_files = os.listdir(speaker_info_dir)
        for file in sorted(speaker_files):
            if file.startswith('@') or file.startswith('.'):
                continue
            speaker_id = os.path.splitext(file)[0]
            dialect = None
            raised_in = None
            with open(os.path.join(speaker_info_dir, file), 'r', encoding=lang_encodings[lang]) as f:
                for line in f:
                    m = re.match(r'^;DIALECT:([\w ]+)$', line.strip())
                    if m:
                        dialect = m.groups()[0]
                    m = re.match(r'^;RAISED IN:([\w ]+)$', line.strip())
                    if m:
                        raised_in = m.groups()[0]
            if raised_in in ['Peking', 'Beijing']:
                dialect = 'Beijing'
            speaker_dialects[speaker_id] = dialect
            print(speaker_id, raised_in, dialect)
            if dialect in dialect_dictionary_mapping:
                 dictionary = dialect_dictionary_mapping[dialect]
            else:
                dictionary = language_dictionary_mapping[lang]
            speaker_dictionaries[speaker_id] = dictionary
        speaker_dictionaries['default'] = language_dictionary_mapping[lang]
        with open(os.path.join(dictionary_root_dir, f'{lang}_speaker_dictionaries.yaml'), 'w', encoding='utf8') as f:
            yaml.safe_dump(speaker_dictionaries, f)
        all_speaker_dictionaries.update(speaker_dictionaries)
        continue

    if False:
        all_speaker_dictionaries['default'] = os.path.join(dictionary_root_dir, 'english_us_mfa.dict')
        with open(os.path.join(os.path.dirname(dictionary_root_dir), 'gp_speaker_dictionaries.yaml'), 'w', encoding='utf8') as f:
            yaml.safe_dump(all_speaker_dictionaries, f)
    from collections import Counter
    counter = Counter()
    counter.update(speaker_dialects.values())
    print(counter)
    print(sorted(counter.items(), key=lambda x: -x[1]))
    #for k, v in speaker_dialects.items():
    #    print(k, v)