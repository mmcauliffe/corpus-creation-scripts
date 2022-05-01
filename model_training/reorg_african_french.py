import os

corpus_root = r'D:\Data\speech\french_corpora\African_Accented_French'
speech_dir = os.path.join(corpus_root, 'speech')


for folder in ['dev', 'test', 'devtest', 'train']:
    folder_path = os.path.join(speech_dir, folder)
    if not os.path.exists(speech_dir):
        continue

    for sub_corpus in os.listdir(folder_path):
        sub_corpus_output = os.path.join(corpus_root, sub_corpus)
        os.makedirs(sub_corpus_output, exist_ok=True)
        transcript_path = os.path.join(corpus_root, 'transcripts', folder, sub_corpus, 'transcripts.txt')
        if not os.path.exists(transcript_path):
            transcript_path = os.path.join(corpus_root, 'transcripts', folder, sub_corpus, 'prompts.txt')
        audio_dir = os.path.join(corpus_root,'speech', folder,  sub_corpus)
        transcripts = {}
        speakers = {}
        with open(transcript_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                wav_path, text = line.split(maxsplit=1)
                splits = wav_path.split('/')
                file_name = wav_path.split('/')[-1]
                if ".wav" in file_name or '.tdf' in file_name:
                    utt = os.path.splitext(file_name)[0]
                else:
                    utt = file_name
                if len(splits)> 1:
                    speaker =splits[-2]
                    out_dir = os.path.join(sub_corpus_output, speaker)
                    with open(os.path.join(out_dir, utt +'.lab'), 'w', encoding='utf8') as outf:
                        outf.write(text)
                elif sub_corpus == 'ca16':
                    print(utt)
                    new_splits = utt.replace('.tdf', '').split('_')
                    speaker = new_splits[-3]
                    out_dir = os.path.join(sub_corpus_output, speaker)

                    if utt.startswith('afc-gabon'):
                        os.makedirs(out_dir,exist_ok=True)
                        with open(os.path.join(out_dir, utt +'.lab'), 'w', encoding='utf8') as outf:
                            outf.write(text)

                transcripts[utt] = text
        print(transcripts)
        for speaker in os.listdir(audio_dir):
            speaker_dir = os.path.join(audio_dir, speaker)
            if not os.path.isdir(speaker_dir):
                continue
            out_dir = os.path.join(sub_corpus_output, speaker)
            os.makedirs(out_dir, exist_ok=True)
            for file in os.listdir(speaker_dir):
                print(file)
                utt = os.path.splitext(file)[0]
                try:
                    text = transcripts[utt]
                    with open(os.path.join(out_dir, utt +'.lab'), 'w', encoding='utf8') as outf:
                        outf.write(text)
                except KeyError:
                    pass
                if not os.path.exists(os.path.join(out_dir, file)):
                    os.rename(os.path.join(speaker_dir, file), os.path.join(out_dir, file))