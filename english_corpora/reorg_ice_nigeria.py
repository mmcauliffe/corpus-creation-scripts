import re

from pathlib import Path
import pympi
import csv
root_directory = Path(r"D:\Data\speech\english_corpora\ICE-Nigeria")

subsections = ["broadcast interviews", "broadcast talks", "business transactions", "class lessons", "commentaries",
               "cross examinations", "legal presentations", "parliamentary debates", "phone calls", "unscripted speeches"]

transcription_dir = root_directory.joinpath("xml", "spoken")
audio_dir = root_directory.joinpath("raw", "spoken")

speaker_file = root_directory.joinpath('participants_ICE_Nigeria.csv')
file_to_speaker_mapping = {}
with open(speaker_file) as f:
    reader = csv.reader(f)
    for i,line in enumerate(reader):
        if i == 0:
            continue
        print(line)
        gender = line.pop(0)
        age = line.pop(0)
        ethnic_group = line.pop(0)
        occupation = line.pop(0)
        files = []
        while True:
            try:
                file_name = line.pop(0)
            except IndexError:
                break
            if not file_name:
                break
            files.append(file_name)
        speaker_id = None
        for f in files:
            m = re.search(r'(?P<file_name>.*) \(sp ?(?P<speaker_number>\d+)\)', f)
            id_in_file = 1
            file_name = f
            if m:
                file_name = m.group('file_name')
                id_in_file = int(m.group('speaker_number'))
            print(f, m)
            if speaker_id is None:
                speaker_id = f"{file_name}_{id_in_file}"
            file_to_speaker_mapping[(file_name, id_in_file)] = speaker_id
        print(speaker_id, gender, age, ethnic_group, occupation, files)

for k, v in file_to_speaker_mapping:
    print(k)
    print(v)

for s in transcription_dir.iterdir():
    print(s)
    output_dir = audio_dir.joinpath(s.name)
    for eaf_file in s.iterdir():
        print(eaf_file)
        tg = pympi.Eaf(file_path=eaf_file).to_textgrid()
        to_remove = []
        for tier in tg.tiers:
            if 'Transcription' not in tier.name:
                to_remove.append(tier.name)
                continue
            print(tier.name)
            m = re.search(r'Transcription (?P<id>\d+)', tier.name)
            id_in_file = 1
            if m:
                id_in_file = int(m.group('id'))
            file_name = eaf_file.name.replace('.eaf', '')
            try:
                speaker_id = file_to_speaker_mapping[(file_name, id_in_file)]
            except:
                speaker_id = f"{file_name}_{id_in_file}"

            print(speaker_id)
            tg.change_tier_name(tier.name, speaker_id)
        for t_name in to_remove:
            tg.remove_tier(t_name)

        tg.to_file(output_dir.joinpath(eaf_file.name.replace('.eaf', '.TextGrid')))