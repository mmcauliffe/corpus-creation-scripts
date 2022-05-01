import os
import shutil

data_dir = r"D:\Data\speech\mls_italian"
output_dir = os.path.join(data_dir, 'train', 'corpus')

for file_name in os.listdir(data_dir):
    if not file_name.endswith('.flac'):
        continue
    name = os.path.splitext(file_name)[0]
    speaker, utt = name.split('_',maxsplit=1)
    speaker_dir = os.path.join(output_dir, speaker)
    shutil.move(os.path.join(data_dir, file_name), os.path.join(speaker_dir, f"{utt}.flac"))