import os


corpus_root = '/mnt/d/Data/speech/swahili_corpora/data_broadcastnews_sw'


for folder in ['test', 'train']:
    folder_path = os.path.join(corpus_root, 'data', folder)
    if not os.path.exists(folder_path):
        continue
    speakers = {}
    transcript_path = os.path.join(folder_path, 'text')
    utt2spk_path = os.path.join(folder_path, 'utt2spk')
    with open(utt2spk_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utterance, speaker = line.split(maxsplit=1)
            speakers[utterance] = speaker
    with open(transcript_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            utterance, text = line.split(maxsplit=1)
            speaker = speakers[utterance]
            print(utterance,  speaker)
            speaker_dir = os.path.join(folder_path, 'wav5', speaker)
            if not os.path.exists(speaker_dir):
                speaker_dir = os.path.join(folder_path, 'wav', speaker)
            with open(os.path.join(speaker_dir, f'{utterance}.lab'), 'w', encoding='utf8') as outf:
                outf.write(text)