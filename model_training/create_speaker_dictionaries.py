import collections
import os
import sys
import subprocess
import yaml

if sys.platform == 'win32':
    training_root = r'D:/Data/speech/model_training_corpora'
    dictionary_dir = r'C:/Users/micha/Documents/Dev/mfa-models/dictionary/training'
else:
    training_root = r'/mnt/d/Data/speech/model_training_corpora'
    dictionary_dir = r'/mnt/c/Users/micha/Documents/Dev/mfa-models/dictionary/training'

languages = ['bulgarian', 'english', 'french', 'german', 'portuguese', 'polish', 'turkish',
             'croatian', 'swedish', 'korean', 'thai', 'mandarin', 'tamil',
             'czech', 'japanese', 'vietnamese', 'ukrainian', 'swahili', 'spanish',
             'russian', 'hausa']

languages = ['spanish']

dialect_dictionary_mapping = {
    'vietnamese':{'north': os.path.join(dictionary_dir, 'vietnamese_hanoi_mfa.dict'),
     'south': os.path.join(dictionary_dir, 'vietnamese_ho_chi_minh_city_mfa.dict'), }
}

default_language_dictionary_mapping = {
    'bulgarian': os.path.join(dictionary_dir, 'bulgarian_mfa.dict'),
    'croatian': os.path.join(dictionary_dir, 'croatian_mfa.dict'),
    'czech': os.path.join(dictionary_dir, 'czech_mfa.dict'),
    'french': os.path.join(dictionary_dir, 'french_mfa.dict'),
    'english': os.path.join(dictionary_dir, 'english_mfa.dict'),
    'german': os.path.join(dictionary_dir, 'german_mfa.dict'),
    'hausa': os.path.join(dictionary_dir, 'hausa_mfa.dict'),
    'japanese': os.path.join(dictionary_dir, 'japanese_mfa.dict'),
    'korean': os.path.join(dictionary_dir, 'korean_hangul_mfa.dict'),
    'mandarin': os.path.join(dictionary_dir, 'mandarin_china_mfa.dict'),
    'polish': os.path.join(dictionary_dir, 'polish_mfa.dict'),
    'portuguese': os.path.join(dictionary_dir, 'portuguese_portugal_mfa.dict'),
    'russian': os.path.join(dictionary_dir, 'russian_mfa.dict'),
    'spanish': os.path.join(dictionary_dir, 'spanish_mfa.dict'),
    'swahili': os.path.join(dictionary_dir, 'swahili_mfa.dict'),
    'swedish': os.path.join(dictionary_dir, 'swedish_mfa.dict'),
    'tamil': os.path.join(dictionary_dir, 'tamil_mfa.dict'),
    'thai': os.path.join(dictionary_dir, 'thai_mfa.dict'),
    'turkish': os.path.join(dictionary_dir, 'turkish_mfa.dict'),
    'ukrainian': os.path.join(dictionary_dir, 'ukrainian_mfa.dict'),
    'vietnamese': os.path.join(dictionary_dir, 'vietnamese_mfa.dict'),
    'hindi-urdu': os.path.join(dictionary_dir, 'hindi-urdu_mfa.dict'),
    'serbo-croatian': os.path.join(dictionary_dir, 'serbo-croatian_mfa.dict'),
    #'Wu': os.path.join(dictionary_dir, 'wu_mfa.dict'),
}

combined_languages = {
    'vietnamese': ['vietnamese_hue_mfa.dict',
                   'vietnamese_hanoi_mfa.dict',
                   'vietnamese_ho_chi_minh_city_mfa.dict'],
    'portuguese': ['portuguese_brazil_mfa.dict', 'portuguese_portugal_mfa.dict'],
    'spanish': ['spanish_latin_america_mfa.dict', 'spanish_spain_mfa.dict'],
    'english': ['english_us_mfa.dict', 'english_uk_mfa.dict', 'english_nigeria_mfa.dict', 'english_india_mfa.dict'],
    'hindi-urdu': ['hindi_mfa.dict', 'urdu_mfa.dict'],
    'serbo-croatian': ['serbo-croatian_croatian_mfa.dict', 'serbo-croatian_serbian_mfa.dict'],

}

default_corpus_dictionary_mapping = {
    'globalphone_portuguese': os.path.join(dictionary_dir, 'portuguese_brazil_mfa.dict'),
    'mtedx_pt': os.path.join(dictionary_dir, 'portuguese_portugal_mfa.dict'),
    'globalphone_spanish': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'm_ailabs_spanish': os.path.join(dictionary_dir, 'spanish_spain_mfa.dict'),
    'mtedx_es': "default",
    'mls_spanish': os.path.join(dictionary_dir, 'spanish_spain_mfa.dict'),
    'google_venezuela': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'google_puerto_rico': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'google_peru': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'google_chile': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'google_columbia': os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict'),
    'common_voice_mandarin_taiwan': os.path.join(dictionary_dir, 'mandarin_taiwan_mfa.dict'),
    'common_voice_mandarin_china': os.path.join(dictionary_dir, 'mandarin_china_mfa.dict'),
    'coraal': os.path.join(dictionary_dir, 'english_us_mfa.dict'),
    'librispeech_english': os.path.join(dictionary_dir, 'english_us_mfa.dict'),
    'google_nigeria': os.path.join(dictionary_dir, 'english_nigeria_mfa.dict'),
    'ICE_Nigeria': os.path.join(dictionary_dir, 'english_nigeria_mfa.dict'),
    'Pakistani_English_Scripted': os.path.join(dictionary_dir, 'english_india_mfa.dict'),
    'google_uk_ireland': os.path.join(dictionary_dir, 'english_uk_mfa.dict'),
    'aru_english': os.path.join(dictionary_dir, 'english_uk_mfa.dict'),
    'nchlt_english': os.path.join(dictionary_dir, 'english_uk_mfa.dict'),
    'vivos': os.path.join(dictionary_dir, 'vietnamese_ho_chi_minh_city_mfa.dict'),
    'aidatatang': os.path.join(dictionary_dir, 'mandarin_china_mfa.dict'),
    'aishell': os.path.join(dictionary_dir, 'mandarin_china_mfa.dict'),
    'thchs30': os.path.join(dictionary_dir, 'mandarin_china_mfa.dict'),
    'common_voice_hindi': os.path.join(dictionary_dir, 'hindi_mfa.dict'),
    'musc2021_cs_hindi': os.path.join(dictionary_dir, 'hindi_mfa.dict'),
    'musc2021_hindi': os.path.join(dictionary_dir, 'hindi_mfa.dict'),
    'common_voice_urdu': os.path.join(dictionary_dir, 'urdu_mfa.dict'),
    'common_voice_serbian': os.path.join(dictionary_dir, 'serbo-croatian_serbian_mfa.dict'),
    'globalphone_croatian': os.path.join(dictionary_dir, 'serbo-croatian_croatian_mfa.dict'),
    'ParlaSpeech': os.path.join(dictionary_dir, 'serbo-croatian_croatian_mfa.dict'),
    'voxpopuli_serbian': os.path.join(dictionary_dir, 'serbo-croatian_croatian_mfa.dict'),
}

language_dialect_detection = {
    'spanish': (['España'], os.path.join(dictionary_dir, 'spanish_spain_mfa.dict'),
                os.path.join(dictionary_dir, 'spanish_latin_america_mfa.dict')),
    'portuguese': (['Portugal'], os.path.join(dictionary_dir, 'portuguese_portugal_mfa.dict'),
                os.path.join(dictionary_dir, 'portuguese_brazil_mfa.dict')),
    'english': (['United States'], os.path.join(dictionary_dir, 'english_us_mfa.dict'),
                os.path.join(dictionary_dir, 'english_uk_mfa.dict')),

}


def load_speaker_tsv(path):
    speaker_data = {}
    with open(path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.split('\t')
            speaker = line[0]
            try:
                dialect = line[3]
            except IndexError:
                dialect = ''
            if dialect == 'Porto':
                dialect = 'Portugal'
            elif dialect == 'Mother tounge':
                dialect = ''
            speaker_data[speaker] = dialect
    return speaker_data

def combine_dictionaries(lang, out_path):
    line_set = set()
    with open(out_path, 'w', encoding='utf8') as outf:
        for dict_name in combined_languages[lang]:
            with open(os.path.join(dictionary_dir, dict_name), 'r', encoding='utf8') as f:
                for line in f:
                    if line not in line_set:
                        outf.write(line)
                        line_set.add(line)


if __name__ == '__main__':
    for lang in languages:
        if lang == 'japanese':
            continue
        print(lang)
        language_root = os.path.join(training_root, lang)
        default_dictionary_path = default_language_dictionary_mapping[lang]

        if lang in combined_languages:
            combine_dictionaries(lang, default_dictionary_path)
        speaker_dictionary_mapping = {}

        temporary_directory = os.path.join(language_root, 'validation_temp')
        for corpus in os.listdir(language_root):
            if corpus.endswith('_temp'):
                continue
            corpus_dir = os.path.join(language_root, corpus)
            if not os.path.isdir(corpus_dir):
                continue
            if not os.listdir(corpus_dir):
                continue
            print(corpus)


            corpus_default_dict = default_corpus_dictionary_mapping.get(corpus, default_dictionary_path)
            if corpus_default_dict == "default":
                continue

            load_from_scratch = True
            yaml_file = os.path.join(corpus_dir, f'{lang}_speaker_dictionaries.yaml')
            speaker_info_path = os.path.join(corpus_dir, 'speaker_info.tsv')
            speaker_info_dir = os.path.join(corpus_dir, 'spk')
            if os.path.exists(speaker_info_path):
                dialect_data = load_speaker_tsv(speaker_info_path)
                if lang in combined_languages:
                    for speaker, v in dialect_data.items():
                        #if not v:
                        #    continue
                        if lang in language_dialect_detection:
                            key, dict_path, other_dict_path = language_dialect_detection[lang]
                            if any(k in v for k in key):
                                speaker_dictionary_mapping[speaker] = dict_path
                            elif other_dict_path:
                                speaker_dictionary_mapping[speaker] = other_dict_path
                            else:
                                speaker_dictionary_mapping[speaker] = corpus_default_dict
                        elif lang in dialect_dictionary_mapping:
                            for d, dict_path in dialect_dictionary_mapping[lang].items():
                                if d in v.lower():
                                    speaker_dictionary_mapping[speaker] = dict_path
                                    break
                            else:
                                speaker_dictionary_mapping[speaker] = corpus_default_dict
                        else:
                            speaker_dictionary_mapping[speaker] = corpus_default_dict
                else:
                    for speaker in dialect_data.keys():
                        speaker_dictionary_mapping[speaker] = corpus_default_dict
                load_from_scratch = False
            elif os.path.exists(speaker_info_dir):
                for filename in os.listdir(speaker_info_dir):
                    speaker = filename.split('.')[0]
                    with open(os.path.join(speaker_info_dir, filename), 'r', encoding='utf8') as f:
                        for line in f:
                            if line.startswith(';DIALECT:'):
                                dialect = line.strip().replace(';DIALECT:', '')
                                print(speaker, dialect)
                                for d, dict_path in dialect_dictionary_mapping[lang].items():
                                    if d in dialect.lower():
                                        speaker_dictionary_mapping[speaker] = dict_path
                                break
                load_from_scratch = False
            elif os.path.exists(yaml_file):
                with open(yaml_file, 'r', encoding='utf8') as f:
                    d = yaml.safe_load(f)
                    for k, v in d.items():
                        v = v.replace('_ipa', '_mfa').replace('_castilian','_spain')
                        if v != corpus_default_dict:
                            if os.path.basename(v) == os.path.basename(default_dictionary_path):
                                v = default_dictionary_path
                            else:
                                v = os.path.join(dictionary_dir, os.path.basename(v))
                        speaker_dictionary_mapping[k] = v
                    load_from_scratch = False
            if load_from_scratch:
                from montreal_forced_aligner.corpus.acoustic_corpus import AcousticCorpus
                from montreal_forced_aligner.db import Speaker
                corpus = AcousticCorpus(corpus_directory=corpus_dir)
                corpus.delete_database()
                corpus.clean_working_directory()
                corpus._load_corpus()
                corpus_speaker_dicts = {}
                with corpus.session() as session:
                    speakers = session.query(Speaker.name)
                for speaker, in speakers:
                    speaker_dictionary_mapping[speaker] = corpus_default_dict
                    corpus_speaker_dicts[speaker] = corpus_default_dict
                with open(yaml_file, 'w', encoding='utf8') as f:
                    yaml.safe_dump(corpus_speaker_dicts, f, allow_unicode=True)
        speaker_dictionary_mapping = {k: v for k, v in speaker_dictionary_mapping.items() if v != default_dictionary_path and k != "default"}
        with open(os.path.join(language_root, f'{lang}_speaker_dictionaries.yaml'), 'w', encoding='utf8') as f:
            yaml.safe_dump(speaker_dictionary_mapping, f, allow_unicode=True)
        c = collections.Counter(os.path.basename(x) for x in speaker_dictionary_mapping.values())