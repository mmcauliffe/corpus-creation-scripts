import os


bad_file_path = r"D:\Data\temp\urdu_bad_files.txt"

with open(bad_file_path) as f:
    for line in f:
        line = line.replace('"','').strip()
        if os.path.exists(line):
            os.remove(line)
        lab_path = line.replace('.wav', '.lab')
        if os.path.exists(lab_path):
            os.remove(lab_path)
        lab_path = line.replace('.wav', '.TextGrid')
        if os.path.exists(lab_path):
            os.remove(lab_path)