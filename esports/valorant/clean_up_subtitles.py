import os
from praatio import tgio
from num2words import num2words
import decimal
import re

multiword_mappings = {
    '[ __ ]': '',
    'claudine white': 'cloud9 white',
    'a evil cat': 'aevilcat',
    'tanner metro': 'tannermetro',
    'leah panda': 'leahpanda',
    'leah pandas': "leahpanda's",

}

mapping = {
    '-': '',
    'breech': 'breach',
    'vcc': 'vct',
    'athena': 'athxna',
    'sagitting': 'sajedene',
    'genji': 'gen g',
    'valerant': 'valorant',
    'dualist': 'duelist',

}

conditional_replacements = {
    ('Game_Changers', 'TSM'): {'kat': 'cath', 'kath': 'cath',},

}

acceptable_values = set(mapping.values())
acceptable_values.update(
    ['gx3'])
acceptable_values.update([x + "'s" for x in acceptable_values])

raw_dir = r'D:\Data\speech\esports\valorant\raw'
output_dir = r'D:\Data\speech\esports\valorant\cleaned'


sub_dirs = [
    r'game_changers',
    r'platchat_valorant'
]

multiword_checks = [
                    ]

for folder in sub_dirs:
    root = os.path.join(raw_dir, folder)
    out_dir = os.path.join(output_dir, folder)
    os.makedirs(out_dir, exist_ok=True)
    files = os.listdir(root)
    for i, file in enumerate(files):
        if not file.endswith('.TextGrid'):
            #if file.endswith('.flac'):
            #    os.symlink(os.path.join(root, file), os.path.join(out_dir, file))
            #    error
            continue
        print(file, i, len(files))
        textgrid_path = os.path.join(root, file)
        out_textgrid_path = os.path.join(out_dir, file)
        tg = tgio.openTextgrid(textgrid_path)
        new_tg = tgio.Textgrid()
        tier_name = tg.tierNameList[0]
        tier = tg.tierDict[tg.tierNameList[0]]
        word_tier = tgio.IntervalTier(tier_name, [], 0, tg.maxTimestamp)
        filtered_intervals = []
        for interval in tier.entryList:
            text = interval.label.lower()
            if text.startswith('[') and text.endswith(']'):
                continue
            text = text.split()
            if len(text) == 1 and filtered_intervals:
                text = filtered_intervals[-1][2].split() + text
                filtered_intervals[-1] = (filtered_intervals[-1][0], interval.end, ' '.join(text))
            else:
                filtered_intervals.append((interval.start, interval.end, ' '.join(text)))

        # second pass

        for i, interval in enumerate(filtered_intervals):
            text = interval[2]
            for x, r in multiword_mappings.items():
                if x in text:
                    text = re.sub(r'(?<= ){}(?= )'.format(re.escape(x)), r, text)
                    text = re.sub(r'^{}(?= )'.format(re.escape(x)), r, text)
                    text = re.sub(r'(?<= ){}$'.format(re.escape(x)), r, text)
                    text = re.sub(r'^{}$'.format(re.escape(x)), r, text)
            text = text.split()
            if i != len(filtered_intervals) - 1:
                next_text = filtered_intervals[i + 1][2]
                next_text = next_text.split()
                combined = text[-1] + ' ' + next_text[0]
                if len(text) == 1:
                    more_combined = None
                else:
                    more_combined = text[-2] + ' ' +text[-1] + ' ' + next_text[0]
                if combined in multiword_mappings:
                    text[-1] = multiword_mappings[combined]
                    next_text = next_text[1:]
                    filtered_intervals[i + 1] = (filtered_intervals[i + 1][0],
                                                 filtered_intervals[i + 1][1],
                                                 ' '.join(next_text))
                elif more_combined in multiword_mappings:
                    text = text[:-1]
                    text[-1] = multiword_mappings[more_combined]
                    next_text = next_text[1:]
                    filtered_intervals[i + 1] = ( filtered_intervals[i + 1][0],
                                                  filtered_intervals[i + 1][1],
                                                  ' '.join(next_text))
                #elif text[-1] in multiword_checks:
                #    print('Combination')
                #    print(text)
                #    print(next_text)
                #    print(combined)
                #elif next_text[0] in multiword_checks:
                #    print('Combination')
                #    print(text)
                #    print(next_text)
                #    print(combined)
            filtered_intervals[i] = (interval[0], interval[1], ' '.join(text))

        for ind, interval in enumerate(filtered_intervals):
            text = interval[2]
            if "[ __ ]" in text:
                text = text.replace("[ __ ]", '')
            text = text.split()
            new_label = []
            for t in text:
                if not t:
                    continue
                try:
                    if re.search(r'[,]$', t):
                        t = t[:-1]
                    for k, v in conditional_replacements.items():
                        conditional_check = True
                        for conditional in k:
                            if conditional not in file:
                                conditional_check = False
                                break
                        if not conditional_check:
                            continue
                        if t in v:
                            t = v[t]
                    if t in mapping:
                        t = mapping[t]
                    elif "'" in t:
                        pre, suf = t.split("'", maxsplit=1)
                        if pre in mapping:
                            t = mapping[pre] + "'" + suf
                    elif "-" in t:
                        pre, suf = t.split("-", maxsplit=1)
                        if pre in mapping:
                            t = mapping[pre] + "-" + suf

                    if not re.search(r'\d', t):
                        new_label.append(t)
                        continue

                    if re.match(r'^\$[\d,]+$', t):
                        t = t[1:].replace(',', '')
                        t = num2words(t)
                        if t == 'one':
                            t += ' dollar'
                        else:
                            t += ' dollars'
                    elif re.match(r'^\$0\.\d+$', t):
                        t = t.split('.')[-1]
                        t = num2words(t)
                        if t == 'one':
                            t += ' cent'
                        else:
                            t += ' cents'
                    elif re.match(r'^\d+[%]$', t):
                        t = t[:-1]
                        t = num2words(t)
                        t += ' percent'
                    elif re.match(r'^\d+\.\d+[%]$', t):
                        t = t[:-1]
                        nums = t.split('.')
                        t = ' point '.join([num2words(x) for x in nums])
                        t += ' percent'
                    elif re.match(r'^\d+[kK]$', t):
                        t = t[:-1]
                        t = num2words(t)
                        t += ' k.'
                    elif re.match(r'^\d+\.\d+[kK]$', t):
                        t = t[:-1]
                        nums = t.split('.')
                        t = ' point '.join([num2words(x) for x in nums]) + ' k.'
                    elif re.match(r'^\d+-\d+$', t):
                        nums = t.split('-')
                        t = [num2words(x) for x in nums]
                        t = ' to '.join(t)
                    elif re.match(r'^\d+-[a-zA-Z]+$', t):
                        t, suffix = t.split('-')
                        t = num2words(t)
                        t += ' ' + suffix
                    elif re.match(r'^\d+:00$', t):
                        t = t[:-3]
                        t = num2words(t)
                    elif re.match(r'^\d+:\d\d$', t):
                        nums = t.split(':')
                        t = [num2words(x) for x in nums]
                        t = ' '.join(t)
                    elif re.match(r'^\dv\d$', t):
                        nums = t.split('v')
                        t = ' v. '.join([num2words(x) for x in nums])
                    elif re.match(r'\d+(th|rd|st|nd)$', t):
                        t = t[:-2]
                        t = num2words(t, to='ordinal')
                    elif re.match(r'^\d+\.\d+$', t):
                        nums = t.split('.')
                        t = ' point '.join([num2words(x) for x in nums])
                    elif re.match(r'^\d+:\d+$', t):
                        nums = t.split(':')
                        t = ' to '.join([num2words(x) for x in nums])
                    elif re.match(r'^[\d,]+$', t):
                        t = num2words(t.replace(',', ''))
                    elif re.match(r'^[-]\d+$', t):
                        t = t[1:]
                        prefix = 'minus '
                        t = prefix + num2words(t)
                    elif re.match(r'^[^0-9]-?\d+$', t):
                        t = t.replace('-', '')
                        prefix = t[0]
                        t = t[1:]
                        t = prefix + '. ' + num2words(t)
                    elif re.match(r'^[^0-9]+-\d+$', t):
                        prefix, t = t.split('-')
                        t = prefix + ' ' + num2words(t)
                    elif re.match(r'^\d+\D$', t):
                        suffix = t[-1]
                        t = t[:-1]
                        t = num2words(t) + ' ' + suffix + '.'
                    elif re.match(r'^\d+(hp|hb|cp|cb|am|pm|ms|hv|mg)$', t):
                        suffix = t[-2]
                        if suffix in ['hb', 'hv']:
                            suffix = 'hp'
                        elif suffix in ['cb']:
                            suffix = 'cp'
                        t = t[:-2]
                        t = num2words(t) + ' ' + suffix
                    elif re.match(r'^\d+(fps|ish)$', t):
                        suffix = t[-3]
                        t = t[:-3]
                        t = num2words(t) + ' ' + suffix
                    if not t or t in ['[', ']', '__']:
                        continue
                    if re.search(r'\d', t) and t not in acceptable_values:
                        print(text)
                        print(new_label)
                        print(t)
                    t = t.replace('/', ' ')
                    new_label.append(t)
                except decimal.InvalidOperation:
                    print(text)
                    print(t)
                    raise
            if False:
                for x in multiword_checks:
                    if x in new_label:
                        print()
                        print('FOUND:', x)
                        if x == new_label[0]:
                            print('PREVIOUS:', word_tier.entryList[-1][2])
                        print('OLD:', text)
                        print('CURRENT:', new_label)
                        if x == new_label[-1] and ind < len(filtered_intervals) - 1:
                            print('NEXT:', filtered_intervals[ind + 1][2])
            new_label = ' '.join(new_label)
            if word_tier.entryList and word_tier.entryList[-1][2] == '' and new_label == '':
                word_tier.entryList[-1] = (word_tier.entryList[-1][0], interval[1], new_label)
            else:
                word_tier.entryList.append((interval[0], interval[1], new_label))
            # print(interval)
        new_tg.addTier(word_tier)
        new_tg.save(out_textgrid_path)
