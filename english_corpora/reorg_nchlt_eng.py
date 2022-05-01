import os
from bs4 import BeautifulSoup as bs
from collections import Counter
root = r'D:\Data\speech\english_corpora\nchlt_eng'

transcription_path = os.path.join(root, 'transcriptions', 'nchlt_eng.tst.xml')

gender_count = Counter()

with open(transcription_path, 'r', encoding='utf8') as f:
    content = bs(f.read(), 'lxml')
    speakers =  content.find_all('speaker')
    for s in speakers:
        print(s.attrs)
        #print(s)
        s_id = 'nchlt_eng_' +s.attrs['id']
        if s.attrs['gender']:
            gender_count[s.attrs['gender']] += 1
            if s.attrs['gender'] == 'male':
                s_id += 'm'
            elif s.attrs['gender'] == 'female':
                s_id += 'f'
        speaker_dir = os.path.join(root, s_id)
        os.makedirs(speaker_dir, exist_ok=True)
        for r in s.find_all('recording'):
            print(r.attrs)
            print(r.text)
            audio_path = os.path.join(os.path.dirname(root), r.attrs['audio'])
            if os.path.exists(audio_path):
                new_audio_path = os.path.join(speaker_dir, os.path.basename(audio_path))
                os.rename(audio_path, new_audio_path)
                with open(new_audio_path.replace('.wav', '.lab'), 'w', encoding='utf8') as f:
                    f.write(r.text)
            else:
                print(audio_path)
                error



print(gender_count)