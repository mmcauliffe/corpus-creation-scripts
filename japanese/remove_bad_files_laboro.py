import os
import shutil
root_dir = r"D:\Data\speech\japanese_corpora\LaboroTVSpeech"

bad_file_path = r"D:\Data\speech\japanese_corpora\bad_files.txt"

bad_files = set()
with open(bad_file_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        bad_files.add(line)

for file in bad_files:
    if file.startswith("MSLT") or file.startswith('common_voice'):
        continue
    directory = os.path.join(root_dir, file)
    if os.path.exists(directory):
        print(file)
        shutil.rmtree(directory)