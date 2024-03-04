import os
import csv
#import nagisa

corpus_root = r'D:\Data\speech\japanese_corpora\magic_data_jp'

audio_dir = os.path.join(corpus_root, 'WAV')

bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';','〈', '〉', '-', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}

tsu_numbers = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十'}

transcriptions = {}
with open(os.path.join(corpus_root, 'UTTRANSINFO.txt'), encoding='utf8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for line in reader:
        transcript = ''.join([x for x in line['TRANSCRIPTION'] if x not in bad_chars])
        utt_id = line['UTTRANS_ID']
        speaker_id = utt_id.split('_',maxsplit=1)[0]
        speaker_directory = os.path.join(audio_dir, speaker_id)
        with open(os.path.join(speaker_directory, utt_id.replace('.wav', '.lab')), 'w', encoding='utf8') as f:
            f.write(transcript)