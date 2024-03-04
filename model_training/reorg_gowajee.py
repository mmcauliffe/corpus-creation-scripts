import os


root_dir = r'D:\Data\speech\model_training_corpora\thai\gowajee'

audio_dir = os.path.join(root_dir, 'audios')

splits = ['dev', 'train', 'test', 'lu']

for s in splits:
    split_dir = os.path.join(root_dir, s)
    transcripts = {}
    utt2spk = {}
    with open(os.path.join(split_dir, 'text'), encoding='utf8') as f:
        for line in f:
            line = line.strip()
            utt, text = line.split(maxsplit=1)
            transcripts[utt] = text

    with open(os.path.join(split_dir, 'utt2spk'), encoding='utf8') as f:
        for line in f:
            line = line.strip()
            utt, spk = line.split(maxsplit=1)
            utt2spk[utt] = spk

    with open(os.path.join(split_dir, 'wav.scp'), encoding='utf8') as f:
        for line in f:
            line = line.strip()
            utt, wav_file_name = line.split()
            wav_path = os.path.join(root_dir, wav_file_name)
            speaker = utt2spk[utt]
            text = transcripts[utt]
            output_dir = os.path.join(root_dir, speaker)
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, utt + '.lab'),'w', encoding='utf8') as outf:
                outf.write(text)
            if os.path.exists(wav_path):
                os.rename(wav_path, os.path.join(output_dir, utt + '.wav'))
