import os
import json
root_dir = r'D:\Data\speech\m_ailabs_corpora'

for lang in os.listdir(root_dir):
    print(lang)
    lang_root = os.path.join(root_dir, lang)
    lang_dir = os.path.join(root_dir, lang, 'by_book')
    for gender in ['female', 'male', 'mix']:
        gender_dir = os.path.join(lang_dir, gender)
        print(gender_dir)
        if not os.path.isdir(gender_dir):
            continue
        if gender == 'mix': # unknown speakers
            for book in os.listdir(gender_dir):
                book_dir = os.path.join(gender_dir, book)
                print(book_dir)
                if not os.path.isdir(book_dir):
                    continue
                with open(os.path.join(book_dir, 'metadata_mls.json'), 'r', encoding='utf8') as f:
                    data = json.load(f)
                wav_dir = os.path.join(book_dir, 'wavs')
                for file_name in os.listdir(wav_dir):
                    text = data[file_name]['clean'].replace('--', ' ')
                    speaker_name = '_'.join(file_name.split('_', maxsplit=2)[:-1])
                    print(speaker_name, file_name, text)
                    speaker_directory = os.path.join(lang_root, speaker_name)
                    os.makedirs(speaker_directory, exist_ok=True)
                    with open(os.path.join(speaker_directory, file_name.replace('.wav', '.lab')), 'w', encoding='utf8') as f:
                        f.write(text)
                    os.rename(os.path.join(wav_dir, file_name), os.path.join(speaker_directory, file_name))
        else:
            for speaker in os.listdir(gender_dir):
                speaker_dir = os.path.join(gender_dir, speaker)
                if not os.path.isdir(speaker_dir):
                    continue
                for book in os.listdir(speaker_dir):
                    book_dir = os.path.join(speaker_dir, book)
                    print(book_dir)
                    if not os.path.isdir(book_dir):
                        continue
                    with open(os.path.join(book_dir, 'metadata_mls.json'), 'r', encoding='utf8') as f:
                        data = json.load(f)
                    wav_dir = os.path.join(book_dir, 'wavs')
                    for file_name in os.listdir(wav_dir):
                        try:
                            text = data[file_name]['clean'].replace('--', ' ')
                        except KeyError:
                            try:
                                text = data[file_name.replace('.wav', '')]['clean'].replace('--', ' ')
                            except KeyError:
                                continue

                        print(speaker, file_name, text)
                        speaker_directory = os.path.join(lang_root, speaker)
                        os.makedirs(speaker_directory, exist_ok=True)
                        with open(os.path.join(speaker_directory, file_name.replace('.wav', '.lab')), 'w', encoding='utf8') as f:
                            f.write(text)
                        os.rename(os.path.join(wav_dir, file_name), os.path.join(speaker_directory, file_name))