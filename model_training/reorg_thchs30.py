import os


corpus_root = r'D:\Data\speech\model_training_corpora\mandarin\data_thchs30'
data_root = r'D:\Data\speech\model_training_corpora\mandarin\data_thchs30/data'


for file in os.listdir(data_root):
    speaker = file.split('_')[0]
    out_dir = os.path.join(corpus_root, speaker)
    os.makedirs(out_dir, exist_ok=True)
    if file.endswith('.wav') and not os.path.exists(os.path.join(out_dir, file)):
        os.rename(os.path.join(data_root, file), os.path.join(out_dir, file))
    elif file.endswith('.wav.trn'):
        print(file)
        with open(os.path.join(data_root, file), 'r',  encoding='utf8') as f, \
            open(os.path.join(out_dir, file.replace('.wav.trn', '.lab')), 'w',  encoding='utf8') as outf:
            for line in f:
                data = line.strip()
                print(data)
                outf.write(data)
                break
