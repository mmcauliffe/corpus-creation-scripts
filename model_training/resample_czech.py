import os
import subprocess
root_dir = "D:\Data\speech\czech_corpora\czech_parliament"

for f in os.listdir(root_dir):
    if not f.endswith('.wav'):
        continue
    original_path = os.path.join(root_dir, f)
    temp_path = os.path.join(root_dir, 'temp.wav')
    subprocess.check_call(['sox', original_path,
                           '-t', 'wav',
                           '-r', '16000',
                           temp_path
                           ])
    os.remove(original_path)
    os.rename(temp_path, original_path)