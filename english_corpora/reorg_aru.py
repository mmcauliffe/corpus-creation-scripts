import os
root = r"D:\Data\speech\english_corpora\ARU_Speech_Corpus_v1_0"

transcripts = {}
current_list = 1
current_index = 1
with open(os.path.join(root, 'transcripts.txt')) as f:
    for line in f:
        line = line.strip()
        if line.startswith('List '):
            current_list = int(line.replace('List ', ''))
            current_index = 1
            continue
        transcripts[(current_list, current_index)] = line
        current_index += 1
print(transcripts)

for file in os.listdir(root):
    if not file.endswith('.wav'):
        continue
    speaker, rest = file.split('_', maxsplit=1)
    rest = rest.split(' - ')
    list_num = int(rest[1].replace('List ', ''))
    sentence_num = int(rest[2].replace('Sentence ', ''))
    print(speaker, list_num, sentence_num)
    speaker_directory = os.path.join(root,speaker)
    os.makedirs(speaker_directory, exist_ok=True)
    base_name = f"{speaker}_{list_num}_{sentence_num}"
    text = transcripts[(list_num, sentence_num)]
    with open(os.path.join(speaker_directory, base_name+'.lab'), 'w', encoding='utf8') as f:
        f.write(text)
    os.rename(os.path.join(root, file), os.path.join(speaker_directory, base_name+'.wav'))