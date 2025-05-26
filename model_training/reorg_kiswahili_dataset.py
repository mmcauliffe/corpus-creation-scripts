import os
import csv

root_dir = r"D:\Data\speech\model_training_corpora\swahili\Kiswahili Dataset"

text_file = os.path.join(root_dir, "text", "metadata.csv")

speaker_dir = os.path.join(root_dir, "kiswahili_dataset_speaker")
os.makedirs(speaker_dir, exist_ok=True)

texts = {}

with open(text_file, 'r', encoding='utf8') as f:
    reader = csv.reader(f, delimiter="|")
    for line in reader:
        t = line[1].strip()
        t2 = line[2].strip().rstrip('"').strip()
        if t != t2:
            print(line[0])
            print(repr(t))
            print(repr(t2))
        with open(os.path.join(speaker_dir, f'{line[0].strip()}.lab'), 'w', encoding='utf8') as outf:
            outf.write(t2)

wav_dir = os.path.join(root_dir, "wavs")

files = os.listdir(wav_dir)
for f in files:
    if f.count('-') == 1:
        os.rename(os.path.join(wav_dir, f), os.path.join(speaker_dir, f))
    else:
        new_f = "-".join(f.split('-')[:2]) + '.wav'
        if not os.path.exists(os.path.join(speaker_dir, new_f)):
            os.rename(os.path.join(wav_dir, f), os.path.join(speaker_dir, new_f))



