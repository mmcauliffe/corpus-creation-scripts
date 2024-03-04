
import re
import pathlib
import csv
root_dir = pathlib.Path(r"D:\Data\speech\model_training_corpora\hindi-urdu\shrutilipi_urdu")

for speaker_dir in root_dir.iterdir():
    transcript_file = speaker_dir.joinpath("transcriptions.txt")
    if not transcript_file.exists():
        continue
    with open(transcript_file, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for i, line in enumerate(reader):
            file_name = f'sent_{i+1}.lab'
            text = re.sub(r'\b\d+\b', '',line[1])
            with open(speaker_dir.joinpath(file_name), 'w', encoding='utf8') as outf:
                outf.write(text)