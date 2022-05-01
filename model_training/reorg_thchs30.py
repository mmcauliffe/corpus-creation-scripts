import os


corpus_root = '/mnt/d/Data/speech/chinese_corpora/data_thchs30'
data_root = '/mnt/d/Data/speech/chinese_corpora/data_thchs30/data'


for file in os.listdir(data_root):
    speaker = file.split('_')[0]
    out_dir = os.path.join(corpus_root, speaker)
    os.makedirs(out_dir, exist_ok=True)
    if file.endswith('.wav'):
        os.rename(os.path.join(data_root, file), os.path.join(out_dir, file))
    else:
        with open(os.path.join(data_root, file), 'r',  encoding='utf8') as f, \
            open(os.path.join(out_dir, file.replace('.wav.trn', '.lab')), 'w',  encoding='utf8') as outf:
            data = f.readline(1)
            outf.write(data)
