
import collections

import os

from pathlib import Path
import spacy
import re
import jsonlines
#from montreal_forced_aligner.language_modeling.english import en_spacy

#nlp = en_spacy(accurate=True)
languages = ['english']
working_directory = r'D:\Data\speech\dictionaries\rich_lexicons\english'
corpus_path = r'D:\Data\speech\model_training_corpora\english'
training_path = Path(r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\english_us_mfa.dict")

lexicon = {}

def load_morphemes(lang):
    morph_path = os.path.join(working_directory, f'{lang}_morphs.jsonl')
    with open(morph_path, 'r', encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        morphs = {}
        alternative_forms = []
        for line in reader:
            if any(any(z in x for x in line['definitions']) for z in ['Used as a substitute', 'Alternative form']):
                alternative_forms.append(line)
            else:
                pos_tags = set(line['pos_tags'])
                key = (line['word'], *sorted(pos_tags))
                if key not in morphs:
                    morphs[key] = {'written_forms': set(), 'definitions': set()}
                morphs[key]['written_forms'].update(line['written_forms'])
                morphs[key]['definitions'].update(line['definitions'])
        for line in alternative_forms:
            for d in line['definitions']:
                m = re.search(r'(Alternative form of|Used as a substitute for) (?P<form>\S+)', d)
                if m is None:
                    continue
                alternative_form = m.group("form")
                if (alternative_form, line['pos_tags'][0]) not in morphs:
                    continue
                morphs[(alternative_form, line['pos_tags'][0])]['written_forms'].update(line['written_forms'])
    return morphs

def load_words(lang):
    lexicon_path = os.path.join(working_directory, f'{lang}.jsonl')
    with open(lexicon_path, 'r', encoding='utf8') as f:
        reader = jsonlines.Reader(f)
        lexicon = {}
        for line in reader:
            key = line.pop('key')
            if key[0] not in lexicon:
                lexicon[key[0]] = {}
            if key[1][0] not in lexicon[key[0]]:
                lexicon[key[0]][key[1][0]] = line
    return lexicon

def run_nlp(text):
    print(text)
    if text.isupper():
        text = text.lower()
    doc = nlp(text)
    for w in doc:
        try:
            lemma = w.lemma_
        except:
            print(w.lemma)
            print(w.text)
            print(w.norm)
            print(w.norm_)
            raise
        norm = w.norm_
        morph = str(w.morph)
        pos = w.pos_
        print(w.text, lemma, norm, morph, pos, w.is_oov)
        if pos in {"PUNCT", "X"} or norm == '-':
            continue
        if norm not in prons:
            pos = 'X'
            if nlp.vocab[lemma].is_oov:
                total_oovs[norm] += 1
            else:
                to_g2p_oovs[norm] += 1
            continue
        key = f"{lemma}_{pos}"
        if key not in lexicon:
            lexicon[key] = {'word': lemma, 'pos': pos}
        if norm == lemma.lower():

            lexicon[key]['base_form'] = {}
            if 'us' not in lexicon[key]['base_form'] and norm in prons:
                lexicon[key]['base_form']['us'] = prons[norm]
            elif norm not in prons:
                print(f"MISSING {norm}")
        else:
            if 'forms' not in lexicon[key]:
                lexicon[key]['forms'] = {}
            if morph not in lexicon[key]['forms']:
                lexicon[key]['forms'][morph] = {}
            if norm not in lexicon[key]['forms'][morph]:
                lexicon[key]['forms'][morph][norm] = {}
                if 'us' not in lexicon[key]['forms'][morph][norm] and norm in prons:
                    lexicon[key]['forms'][morph][norm]['us'] = prons[norm]
                elif norm not in prons:
                    print(f"MISSING {norm}")

suffix_normalization = {
    '-ie': '-y',
    '-tic': '-ic',
    '-erie': '-ery',
    '-ers': '-er -s',
    '-sie': '-s -y',
    '-ally': '-al -ly',
    '-ise': '-ize',
    '-isation': '-ization',
    '-ization': '-ize -ation',
    '-ibility': '-ability',
    '-ability': '-able + -ity',
    '-ification': '-ify -ation',
    'back-': 'back',
    'after-': 'after',
    '-burger': 'burger',
}

monomorphemic_overrides = {'feed', 'number',  'awesome','awkward', 'baby', 'sight','weed','yes'}

def break_up_morpheme(m):
    if m in monomorphemic_overrides or m not in morphological_strings:
        return [m]
    new_s = []
    more_morphs = list(morphological_strings[m])[0]
    if isinstance(more_morphs, str):
        more_morphs = more_morphs.split()
    for ms in more_morphs:
        new_s.extend(break_up_morpheme(ms))
    return new_s



if __name__ == '__main__':
    for lang in languages:
        morphs = load_morphemes(lang)
        words = load_words(lang)
        morphological_strings = collections.defaultdict(set)
        unparsed = 0
        inflections = set()
        for k, v in words.items():
            for pos, data in v.items():
                if 'inflections' in data:
                    for inflection, string in data['inflections'].items():
                        if string != k:
                            inflections.add(string)
        inflection_pos_mapping = {}
        for k, v in words.items():
            if k in inflections:
                continue
            for pos, data in v.items():
                skip = False
                for d in data['definitions']:
                    if 'plural of ' in d.lower():
                        skip = True
                        break
                if skip:
                    continue
                actual_form = k
                if len(data['definitions']) == 1:
                    d = data['definitions'][0].lower()
                    if '(obsolete' in d:
                        continue
                    d = re.sub(r'\.? ?(\[.*])?$', '', d)
                    if re.search(r'(obsolete|rare|archaic|nonstandard) (spelling|form)', d):
                        actual_form = re.sub(r'(obsolete|rare|archaic|nonstandard) (spelling|form) of ', '', d)
                actual_form += f' {pos}'
                if 'morphological_string' not in data or any(data['morphological_string'].startswith(x) for x in ['From Ancient Greek',
                    'Ancient Greek', 'Old English', 'Middle French', 'Old French', 'Blend of', 'First attested', 'From Latin', 'Latin', 'From New Latin', 'New Latin', 'Borrowed', 'Clipped',
                    'From Byzantine Greek','Byzantine Greek', 'Italian', 'From Italian', 'From blend', 'From Blend',
                    'From Late Latin', 'Late Latin', "From Late Middle", "Late Middle", "From late Middle", "late Middle",
                    'From Old English', 'From Middle English', 'From Middle French','From Old French','From French']):
                    if 'inflections' in data:
                        for inflection, string in data['inflections'].items():
                            morph = None
                            if inflection == 'plural' and string.endswith('s') and string != k:
                                morph = "-s"
                            elif inflection == "3|s|pres" and string.endswith('s') and string != k:
                                morph = "-s"
                            elif inflection == "gerund" and string.endswith('ing') and string != k:
                                morph = "-ing"
                            elif inflection == "past" and string.endswith('ed') and string != k:
                                morph = "-ed"
                            elif inflection == "comparative" and string.endswith('er') and string != k:
                                morph = "-er"
                            elif inflection == "superlative" and string.endswith('est') and string != k:
                                morph = "-est"
                            if morph is not None:
                                morphological_strings[f"{string}"].add(tuple([actual_form, morph]))
                    continue
                morph = re.sub(r'^From ', '', data['morphological_string'])
                morph = re.sub(r'\.$', '', morph)
                morph = re.sub(r' \(.*?\)\)?', '', morph)
                morph = re.sub(r', .*?,', '', morph)
                morph.replace('’', '')
                key = f"{k} {pos}"
                prefix_suffix_m = re.search(r"(?P<prefix>([a-zA-Z']+-\s+\+?\s*)+)(?P<suffix>(\+?\s+-[a-zA-Z']+)+)", morph)
                prefix_m = re.search(r"(?P<prefix>([a-zA-Z']+-\s*\+)+)\s*(?P<stem>['a-zA-Zá]+)\s*(?P<suffix>(\+\s+-[a-zA-Z']+)+)?", morph)
                suffix_m = re.search(r"(?P<stem>[a-zA-Zá']+)\s*(?P<suffix>(\+\s+-[a-zA-Z']+)+)", morph)
                compound_m = re.search(r"(?P<word_one>[a-zA-Zá']+)\s*\+\s*(?P<word_two>[a-zA-Zá']+)", morph)
                if prefix_suffix_m:
                    prefixes = [x for x in prefix_suffix_m.group('prefix').strip().split() if x and x != '+']
                    suffixes = [x for x in prefix_suffix_m.group('suffix').strip().split() if x and x != '+']
                    suffixes = [x if x not in suffix_normalization else suffix_normalization[x] for x in suffixes]
                    morphological_strings[key].add((*prefixes, *suffixes))
                elif prefix_m and not (prefix_m.group('stem') == 'Latin' and 'Latin' not in k):
                    prefixes = [x for x in prefix_m.group('prefix').strip().split() if x and x != '+']

                    if prefix_m.group('suffix'):
                        suffixes = [x for x in suffix_m.group('suffix').strip().split() if x and x != '+']
                        suffixes = [x if x not in suffix_normalization else suffix_normalization[x] for x in suffixes]
                    else:
                        suffixes = []

                    morphological_strings[key].add((*prefixes, prefix_m.group('stem'), *suffixes))
                elif suffix_m and not (suffix_m.group('stem') == 'Latin' and 'Latin' not in k):
                    suffixes = [x for x in suffix_m.group('suffix').strip().split() if x and x != '+']
                    suffixes = [x if x not in suffix_normalization else suffix_normalization[x] for x in suffixes]
                    morphological_strings[key].add((suffix_m.group('stem'), *suffixes))
                elif compound_m and not (compound_m.group('word_one') == 'Latin' and 'Latin' not in k) and not (compound_m.group('word_two') == 'Latin' and 'Latin' not in k):
                    morphological_strings[key].add((compound_m.group('word_one'), compound_m.group('word_two')))
                else:
                    print(k, morph, prefix_m)
                    unparsed += 1
                if 'inflections' in data:
                    for inflection, string in data['inflections'].items():
                        if key in morphological_strings:
                            for s in morphological_strings[key]:
                                morph = None
                                if inflection == 'plural' and string.endswith('s') and string != k:
                                    morph = "-s"
                                elif inflection == "3|s|pres" and string.endswith('s') and string != k:
                                    morph = "-s"
                                elif inflection == "gerund" and string.endswith('ing') and string != k:
                                    morph = "-ing"
                                elif inflection == "past" and string.endswith('ed') and string != k:
                                    morph = "-ed"
                                if morph is not None:
                                    morphological_strings[f"{string} {pos}"].add(tuple(list(s) + [morph]))

        for k,v in morphological_strings.items():
            print(k)
            new_strings = set()
            for s in v:
                new_s = []

                for morpheme in s:
                    new_s.extend(break_up_morpheme(morpheme))
                new_strings.add(' '.join(new_s))
            morphological_strings[k] = new_strings
        with open(os.path.join(working_directory, 'morphological_training_data.txt'),'w', encoding='utf8') as f:
            for k,v in morphological_strings.items():
                for s in v:
                    f.write(f"{k}\t{s}\n")
                #if len(v) > 1:
                #    print(k,v)

        print(len(morphological_strings))
        print("UNPARSED", unparsed)
    if False:
        prons = collections.defaultdict(list)
        total_oovs = collections.Counter()
        to_g2p_oovs = collections.Counter()
        with open(training_path, encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                word, pron = line.split('\t')
                prons[word].append(pron)
        prons["-n't"].append("n̩ t")
        prons["re-"].append("ɹ ɨ")
        prons["-ly"].append("ʎ i")
        prons["-ing"].extend(["ɨ n", "ɨ ŋ"])
        prons["-s"] = {r'[tpckf]$': "s", r'[td]?[zsʃʒ]$': "ɨ z", r'[^tpkfzsʃʒ]$': "z"}
        prons["-ed"] = {r'[sʃfpkθc][̪]?$': "t", r'[td]$': "ɨ d", r'[^tdsʃfpkθc][̪]?$': "d"}
        corpus = AcousticCorpus(corpus_directory=Path(corpus_path))
        print(corpus.num_utterances)
        with corpus.session() as session:
            query = session.query(Utterance).filter(Utterance.text != '').limit(1000)
            for u in query:
                run_nlp(u.text)
        with open(os.path.join(working_directory, 'english_lexicon.json'), 'w', encoding='utf8') as f:
            json.dump(lexicon, f, indent=4,ensure_ascii=False)
        with open(os.path.join(working_directory, 'total_oovs.txt'), 'w', encoding='utf8') as f:
            for k, v in sorted(total_oovs.items(),  key=lambda x: -x[1]):
                f.write(f"{k}\t{v}\n")
        with open(os.path.join(working_directory, 'oovs.txt'), 'w', encoding='utf8') as f:
            for k, v in sorted(to_g2p_oovs.items(),  key=lambda x: -x[1]):
                f.write(f"{k}\t{v}\n")
        #print(lexicon)
