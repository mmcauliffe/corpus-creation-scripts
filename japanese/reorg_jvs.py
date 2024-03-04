import os
#import nagisa

corpus_root = r'D:\Data\speech\japanese_corpora\jvs_ver1'

styles = ['falset10', 'nonpara30', 'parallel100', 'whisper10']

bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';','〈', '〉', '-', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}

tsu_numbers = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十'}

for speaker in os.listdir(corpus_root):
    speaker_dir = os.path.join(corpus_root, speaker)
    if not os.path.isdir(speaker_dir):
        continue
    texts = {}
    for file in os.listdir(speaker_dir):
        if not file.endswith('.wav') and not file.endswith('.lab'):
            continue
        p = file.split('_')
        new_speaker = '_'.join(p[:2])
        new_speaker_dir = os.path.join(speaker_dir, new_speaker)
        os.makedirs(new_speaker_dir, exist_ok=True)
        os.rename(os.path.join(speaker_dir, file), os.path.join(new_speaker_dir, file))
    continue
    for style in styles:
        transcript_path = os.path.join(speaker_dir, style, 'transcripts_utf8.txt')
        wav_folder = os.path.join(speaker_dir, style, 'wav24kHz16bit')
        texts = {}
        with open(transcript_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                utt, text = line.split(':', maxsplit=1)
                new_words = []
                words = nagisa.tagging(text)
                for i, w in enumerate(words.words):
                    if len(new_words) and (new_words[-1].startswith('<') and not new_words[-1].endswith('>')):
                        new_words[-1] += w
                        continue
                    elif len(new_words) and new_words[-1].endswith('っ'):
                        w = 'っ' + w
                        new_words[-1] = new_words[-1][:-1]
                    elif len(new_words) and w == 'つ' and new_words[-1] in tsu_numbers:
                        new_words[-1] += w
                        continue
                    if w in bad_chars:
                        continue
                    new_words.append(w)
                new_text = ' '.join(new_words)
                texts[utt] = new_text
        for file in os.listdir(wav_folder):
            utt = file.split('.')[0]
            if utt not in texts:
                print(speaker, style, utt)
            with open(os.path.join(speaker_dir, f'{speaker}_{style}_{utt}.lab'), 'w', encoding='utf8') as f:
                f.write(texts[utt])

            os.rename(os.path.join(wav_folder, file), os.path.join(speaker_dir, f"{speaker}_{style}_{utt}.wav"))
