import os
import re

import nagisa
japanese_root = r'/mnt/d/Data/speech/Microsoft/japanese'


bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';','〈', '〉', '-', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}

tsu_numbers = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十'}

for folder in ['MSLT_Dev_JA_20170914', 'MSLT_Test_JA_20170914']:
    folder_path = os.path.join(japanese_root, folder)
    for file in os.listdir(folder_path):
        if not file.endswith('.T1.jp.snt'):
            continue

        with open(os.path.join(folder_path, file), 'r', encoding='utf16') as f:
            text = f.read()
        text = text.replace('<SPN/>', '')
        text = text.replace('<LM>', '')
        text = text.replace('</LM>', '')
        words = re.split(r'[\s？、。]+', text)
        new_words = []
        for i, w in enumerate(words):
            w = w.replace('</MP>', '>')
            w = w.replace('</UNSURE>', '>')
            w = w.replace('<UNSURE>', '<')
            if w.startswith('<SU/>'):
                w = f'<{w.replace("<SU/>", "")}>'
            if w.endswith('<EU/>'):
                w = f'<{w.replace("<EU/>", "")}>'
            if "NPS>" in w:
                continue
            if "<NON/>" in w:
                continue
            if "<UNIN/>" in w:
                w = '<UNK>'
            if not w:
                continue
            new_words.append(w)
        new_text = ' '.join(new_words)
        new_words = []
        words = nagisa.tagging(new_text)
        for i, w in enumerate(words.words):
            if len(new_words) and (new_words[-1].startswith('<') and not new_words[-1].endswith('>')):
                new_words[-1] += w
                continue
            elif len(new_words) and new_words[-1].endswith('っ'):
                w = 'っ' + w
                new_words[-1] = new_words[-1][:-1]
            elif len(new_words) and w == 'つ' and new_words[-1] in tsu_numbers:
                new_words[-1] += w
                continue
            if w in bad_chars:
                continue
            new_words.append(w)
        new_text = ' '.join(new_words)
        with open(os.path.join(folder_path, file.replace('.T1.jp.snt', '.T0.jp.lab')), 'w', encoding='utf8') as f:
            f.write(new_text)