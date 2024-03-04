import os

model_training_root = r'D:/Data/speech/model_training_corpora'

languages = {
    'tamil': [
        ('D:/Data/speech/Microsoft/tamil/ms_tamil_train', 'ms_tamil_train'),
        ('D:\Data\speech\CommonVoice\common_voice_tamil', 'common_voice_tamil'),
        (r'D:\Data\speech\tamil_corpora\google_tamil', 'google_tamil'),
        (r'D:\Data\speech\tamil_corpora\mile_tamil_asr_corpus\mile_tamil_train', 'mile_tamil_train'),
    ],
    'english': [
        (r'D:\Data\speech\hindi_corpora\musc2021_cs_hindi', 'musc2021_cs_hindi'),
    ],
    'hindi-urdu': [
        (r'D:\Data\speech\CommonVoice\common_voice_hindi', 'common_voice_hindi'),
        (r'D:\Data\speech\hindi_corpora\musc2021_hindi', 'musc2021_hindi'),
        (r'D:\Data\speech\hindi_corpora\musc2021_cs_hindi', 'musc2021_cs_hindi'),
        (r'D:\Data\speech\CommonVoice\common_voice_urdu', 'common_voice_urdu'),
    ],
    'japanese': [
        (r'D:\Data\speech\japanese_corpora\jvs_ver1', 'jvs'),
        (r'D:\Data\speech\japanese_corpora\tedxjp_10k', 'tedxjp_10k'),
        (r'D:\Data\speech\japanese_corpora\LaboroTVSpeech', 'LaboroTVSpeech'),
        (r'D:\Data\speech\japanese_corpora\magic_data_jp', 'magic_data_jp'),
        (r'D:\Data\speech\CommonVoice\common_voice_japanese', 'common_voice_ja'),
        #(r'D:\Data\speech\GlobalPhone\Japanese\gp_japanese', 'globalphone_ja'),
        (r'D:\Data\speech\Microsoft\japanese', 'microsoft_japanese'),
    ],
}

for lang, links in languages.items():
    lang_dir = os.path.join(model_training_root, lang)
    lang_training = os.path.join(lang_dir, f'{lang}_training')
    os.makedirs(lang_training, exist_ok=True)
    for source, name in links:
        if not os.path.exists(source):
            continue
        dest = os.path.join(lang_training, name)
        if os.path.exists(dest):
            continue
        os.symlink(source, dest, target_is_directory=True)
