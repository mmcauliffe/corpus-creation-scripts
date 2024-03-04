import fugashi
import collections
import jsonlines
from pathlib import Path

root_dir = Path(__file__).resolve().parent
japanese_path = root_dir.joinpath('rich_lexicons', 'japanese.jsonl')

def load_lexicon():
    lexicon = collections.defaultdict(dict)
    with open(japanese_path, encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        for line in reader:
            word, pos = line['key'][0], tuple(line['key'][1])
            line = {k: v for k,v in line.items() if k not in ['word', 'pos_tags', 'key']}
            if word in lexicon and pos in lexicon[word]:
                for other_morph in lexicon[word][pos]:
                    if set(other_morph['written_forms']) == set(line['written_forms']):
                        for d in line['definitions']:
                            if d not in other_morph['definitions']:
                                other_morph['definitions'].append(d)
                        break
                else:
                    lexicon[word][pos].append(line)
            else:
                lexicon[word][pos] = [line]
    return lexicon

if __name__ == '__main__':

    tagger = fugashi.Tagger("-Owakati")
    w = 'おもいださせられちゃわなかったヨ'
    x = tagger.parse(w)
    morpheme_list = []
    for word in tagger(w):
        print(word, word.feature.lemma, word.pos.split(',')[0])
        continue
        if line == 'EOS':
            continue
        line = line.split()
        morpheme = line[0]
        print(line)
        print(line[4])
        tag = line[4].split('-')[0]
        morpheme_list.append(f"{morpheme}_{tag}")
    print(morpheme_list)
    error
    lexicon = load_lexicon()
    for word in lexicon.keys():
        words = nagisa.tagging(word)
        print(word)
        print(words)