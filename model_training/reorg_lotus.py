import os


root_dir = r'D:\Data\speech\model_training_corpora\thai\AIFORTHAI-LotusCorpus\LOTUS'

mapping_file = os.path.join(root_dir, 'Supplement', 'index.txt')
transcript_file = os.path.join(root_dir, 'Supplement', 'PDsen.txt')

audio_root = os.path.join(root_dir, 'PD')

transcripts = {}
with open(transcript_file, encoding='utf8') as f:
    for line in f:
        line = line.strip()
        sentence_id, text, _ = line.split('\t')
        transcripts[sentence_id] = text

utterance_texts = {}

with open(mapping_file, encoding='utf8') as f:
    for line in f:
        if not line.startswith('Pa'):
            continue
        line = line.strip()
        dataset, sequence_number, sentence_id = line.split('\t')
        utterance_texts[(dataset, sequence_number)] = transcripts[sentence_id.strip()]

for letter in os.listdir(audio_root):
    letter_directory = os.path.join(audio_root, letter)
    for setting in os.listdir(letter_directory):
        setting_directory = os.path.join(letter_directory, setting, 'Wav')
        for speaker in os.listdir(setting_directory):
            speaker_directory = os.path.join(setting_directory, speaker)
            speaker, dataset = speaker.split('_')
            output_directory = os.path.join(root_dir, speaker)
            os.makedirs(output_directory, exist_ok=True)
            for wav_file in os.listdir(speaker_directory):
                sequence_number = wav_file.split('.')[0].split('_')[-1]
                text = utterance_texts[(dataset, sequence_number)]
                with open(os.path.join(output_directory, wav_file.replace('.wav', '.lab')), 'w', encoding='utf8') as f:
                    f.write(text)
                os.rename(os.path.join(speaker_directory, wav_file), os.path.join(output_directory, wav_file))