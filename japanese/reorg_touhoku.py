from pathlib import Path
import re

root = Path(r"D:\Data\speech\japanese_corpora\touhoku_folktale")

sound_file_root = root.joinpath("speech")

transcript_root = root.joinpath("transcript", "utf8")

transcripts = {}

tape_speak_mapping = {
    'tape001': 'touhouku_F001',
    'tape060': 'touhouku_M001',
    'tape061': 'touhouku_M001',
}

for tape_path in transcript_root.iterdir():
    tape_name = tape_path.name
    speaker_name = tape_speak_mapping[tape_name]
    speaker_output = root.joinpath(speaker_name)
    speaker_output.mkdir(parents=True, exist_ok=True)
    for csv_file in tape_path.iterdir():
        file_name = csv_file.stem
        with open(csv_file, 'r', encoding='utf8') as f:
            transcript = f.read()
            transcript = re.sub(r'［\w+?］', '', transcript)
            transcript = transcript.replace('｜', '')
            transcript = transcript.replace('\n', ' ')
        lab_path = speaker_output.joinpath(file_name + '.lab')
        with open(lab_path, 'w', encoding='utf8') as f:
            f.write(transcript)
        sound_file = sound_file_root.joinpath(tape_name, file_name + '.wav')
        if sound_file.exists():
            sound_file.rename(speaker_output.joinpath(file_name+'.wav'))


print(transcripts)
