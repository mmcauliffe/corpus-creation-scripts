import os

root = r"D:\Data\speech\japanese_corpora\LaboroTVSpeech\LaboroTVSpeech_v1.0d\data"
output_dir = r"D:\Data\speech\japanese_corpora\LaboroTVSpeech"

recombinations = {
    ('だっ', 'た'),
    ('ん', 'だ'),
    ('し', 'た'),
    ('し', 'て'),
    ('よかっ', 'た'),
    ('ませ', 'ん'),
    ('つか','う'),
    ('じゃ','う'),
    ('う','そっ'),
    ('あら','う'),
    ('違','う'),
    ('違','うっ'),
    ('う','で'),
    ('う','ら'),
    ('う','ぢ'),
    ('う','うん'),
    ('う','がい'),
}


for split in ['dev', 'train']:
    split_dir = os.path.join(root, split)
    transcription_file = os.path.join(split_dir, 'text.v1.0d.csv')
    texts = {}
    with open(transcription_file, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            utt, text = line.split(',')
            words = text.split()
            new_words = []
            for w in words:
                w, pos = w.split('+')
                if w == 'っていう':
                    new_words.append('って')
                    new_words.append('いう')
                    continue
                elif w == 'という':
                    new_words.append('と')
                    new_words.append('いう')
                    continue
                if len(new_words):
                    if (new_words[-1], w) in recombinations:
                        new_words[-1] += w
                        continue
                    if new_words[-1] == 'だっ' and w == 'た':
                        new_words[-1] += w
                        continue
                    elif new_words[-1] == 'ん' and w == 'だ':
                        new_words[-1] += w
                        continue
                    elif len(new_words[-1]) > 2 and new_words[-1].endswith('かっ') and w in {'た'}:
                        w = 'かっ' + w
                        new_words[-1] = new_words[-1][:-2]
                    elif new_words[-1].endswith('っ') and w in {'た', 'て'}:
                        w = 'っ' + w
                        new_words[-1] = new_words[-1][:-1]
                    elif w in {'う', 'うっ'} and new_words[-1][-1] in {'ょ', 'こ', 'ろ', 'そ', 'も', 'よ', 'お', 'ほ', 'つ', '合', 'ご', 'と'}:
                        new_words[-1] += w
                        continue
                    elif  w == 'た' and new_words[-1][-1] in {'し'}:
                        new_words[-1] += w
                        continue
                new_words.append(w)
            new_text = ' '.join(new_words)
            texts[utt] = new_text
    audio_dir = os.path.join(split_dir, 'wav')
    for file in os.listdir(audio_dir):
        print(file)
        utt = os.path.splitext(file)[0]
        try:

            text = texts[utt]
        except KeyError:
            continue
        utt_name = utt.split('_')[-1]
        speaker_dir = os.path.join(output_dir, utt_name)
        os.makedirs(speaker_dir, exist_ok=True)
        with open(os.path.join(speaker_dir, utt_name +'.lab'), 'w', encoding='utf8') as f:
            f.write(text)
        os.rename(os.path.join(audio_dir, utt+'.wav'), os.path.join(speaker_dir, utt_name+'.wav'))

