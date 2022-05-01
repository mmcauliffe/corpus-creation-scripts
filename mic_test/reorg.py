import os
import subprocess
import shutil
data_root = r'D:\Data\speech\benchmark_datasets\mm_mic_test'



for root, dirs, files in os.walk(data_root, followlinks=True):
    for f in files:
        if not f.endswith('.m4a'):
            continue
        video_path = os.path.join(root, f)
        audio_path = video_path.replace('.m4a', '.wav')
        if 'duke' in audio_path:
            input_file = os.path.join(data_root, 'duke.txt')
        else:
            input_file = os.path.join(data_root, 'north_wind.txt')
        lab_file = video_path.replace('.m4a', '.txt')
        shutil.copyfile(input_file, lab_file)
        #if not os.path.exists(audio_path):
        subprocess.call(['ffmpeg', '-i', video_path, '-vn', '-map_channel', '0.0.0', '-sample_fmt', 's16', '-ar', '16000', audio_path])