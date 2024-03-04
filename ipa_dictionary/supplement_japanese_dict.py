import collections

oov_path = r"D:\temp\validate_temp\_validate_training\oovs_found.txt"
japanese_dict_path = r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\japanese_ipa.dict"
output_path = "backup_dictionaries/japanese_ipa.dict"
to_g2p_path = "backup_dictionaries/japanese_to_g2p.txt"
extra_dictionary = "backup_dictionaries/original_japanese.txt"

oovs = set()
with open(oov_path, 'r', encoding='utf8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('＜'):
            continue
        if line.startswith('<'):
            continue
        oovs.add(line)

extra_words = collections.defaultdict(list)
extra_word_set = set()

with open(extra_dictionary, 'r', encoding='utf8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        word = line.split('\t')[0]
        if word not in oovs:
            continue
        extra_word_set.add(word)
        extra_words[word].append(line)


with open(to_g2p_path, 'w', encoding='utf8') as f:
    for w in sorted(oovs - extra_word_set):
        print(w)
        f.write(w +'\n')

with open(output_path, 'w', encoding='utf8') as f:
    for w in oovs:
        if w not in extra_words:
            continue
        for line in extra_words[w]:
            f.write(line + '\n')
