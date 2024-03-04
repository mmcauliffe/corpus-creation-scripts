import os
from bs4 import BeautifulSoup as bs
from montreal_forced_aligner.g2p.generator import PyniniValidator
working_directory = r"/mnt/d/Data/speech/dictionaries/japanese"

name_path = os.path.join(working_directory, "JMnedict.xml")
g2p_path = os.path.join(working_directory, "japanese_mfa.zip")
temp_dir = os.path.join(working_directory, "temp")
output_path = os.path.join(working_directory, "output.dict")
g2p_output_path = os.path.join(working_directory, "output_g2pped.dict")
mapping_output_path = os.path.join(working_directory, "output_mapped.dict")

oovs = "/mnt/d/Data/speech/model_training_corpora/japanese/validation_temp/laborotv/laborotv_validate_training/oovs_found_japanese_mfa.txt"

if __name__ == '__main__':
    dictionary = {}
    if not os.path.exists(output_path):
        g2p = PyniniValidator(g2p_model_path=g2p_path,
                              temporary_directory=temp_dir,
                              num_jobs=3,
                              num_pronunciations=1, quiet=True
                              )
        g2p.setup()
        with open(name_path, 'r', encoding='utf8') as f:
            content = bs(f.read(), features='xml')
        words = content.findAll('entry')
        with open(output_path, 'w', encoding='utf8') as f,\
                open(mapping_output_path, 'w', encoding='utf8') as mappingf:
            for w in words:
                kanji = w.find('keb')
                readings = [x.text for x in w.findAll('reb')]
                if not readings:
                    continue
                if kanji is not None:
                    kanji = kanji.text
                    word = kanji
                else:
                    word = readings[0]
                    kanji = ''
                g2p.word_list = readings
                output = g2p.generate_pronunciations()
                for k, x in output.items():
                    f.write(f"{word}\t{' '.join(x)}\n")
                    mappingf.write(f"{kanji}\t{k}\t{' '.join(x)}\n")
    oov_set = set()
    with open(oovs, 'r', encoding='utf8') as inf:
        for line in inf:
            oov_set.add(line.strip())
    with open(output_path, 'r', encoding='utf8') as inf, open(g2p_output_path, 'w', encoding='utf8') as outf:
        for line in inf:
            word = line.split('\t')[0]
            if word in oov_set:
                outf.write(line)
