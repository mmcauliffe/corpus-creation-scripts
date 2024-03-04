import os
import fugashi
from pathlib import Path
from montreal_forced_aligner.config import MFA_PROFILE_VARIABLE,  GLOBAL_CONFIG
from montreal_forced_aligner.corpus import AcousticCorpus
from montreal_forced_aligner.db import Utterance

working_directory= r'D:/Data/speech/dictionaries/japanese'

output_path = os.path.join(working_directory, 'corpus.txt')

unidic_path = r'D:/Data/speech/dictionaries/japanese/unidic-csj-202302_full'

tagger = fugashi.Tagger(f'{unidic_path} -Owakati')

japanese_corpus_path = r'D:\Data\speech\model_training_corpora\japanese'

if __name__ == '__main__':
    os.environ[MFA_PROFILE_VARIABLE] = "anchor"
    GLOBAL_CONFIG.current_profile.clean = False
    GLOBAL_CONFIG.save()
    corpus = AcousticCorpus(corpus_directory=Path(japanese_corpus_path))
    print(corpus.num_utterances)
    with corpus.session() as session, open(output_path,'w', encoding='utf8') as outf:
        query = session.query(Utterance).filter(Utterance.text != '')#.limit(10)
        for u in query:
            for word in tagger(u.text):
                features = [x if x is not None else '' for x in word.feature]
                features = [x if ',' not in x else f'"{x}"' for x in features]
                feature_text = ','.join(features)
                outf.write(f"{word}\t{feature_text}\n")
            outf.write('EOS\n')
