import os
import re

from praatio.utilities.constants import Interval
from praatio.textgrid import Textgrid, IntervalTier, openTextgrid

root_dir  = r'D:\Data\speech\english_corpora\coraal'

replacements = {
'[ ': '[',
'[<': '[',
'>]': ']',
'.]': ']',
' ]': ']',
'2K': 'two k',
'9:30': 'nine thirty',
'd2D': 'd two d',
'104': 'one oh four',
'ICD-9': 'i c d nine',
'2400': 'twenty four hundred',
'1613': 'sixteen thirteen',
'M1s': 'm ones',
'PS4': 'p s four',
'401k': 'four oh one k',
'50 Cent': 'fifty cent',
'/RD-NAME-3.': '[RD-NAME-3]',
'/RD-NAME- 4/': '[RD-NAME-4]',
'[/RD-NAME-2/-]': '[RD-NAME-2]',
'/[RD-SCHOOL-4/': '[RD-SCHOOL-4]',
'[RD-SCHOOL-3/': '[RD-SCHOOL-3]',
'RD- NAME-3': 'RD-NAME-3',
'/RD-NAME-2,': '[RD-NAME-2]',
'/RD-NAME-2]': '[RD-NAME-2]',
'like/RD-NAME-2/': 'like [RD-NAME-2]',
'And/RD-NAME-2/': 'And [RD-NAME-2]',
'/RD-NAME- 6/': '[RD-NAME-6]',
'into/RD-SCHOOL-2/': 'into [RD-SCHOOL-2]',
'8': 'eight',
'[laugh>_': '[laugh_',
'<laugh]': '[laugh]',
'[laugh>': '[laugh]',
'[laughing]': '[laugh]',
'9': 'nine',
'0': 'zero',
    '12': 'twelve',
    '13': 'thirteen',
    '18': 'eighteen',
}

word_replacements = {
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    '10': 'ten',
    '11': 'eleven',
    '12': 'twelve',
    '13': 'thirteen',
    '14': 'fourteen',
    '14': 'fifteen',
}

bracket_pattern = re.compile(r'(\[.*?])')
slash_pattern = re.compile(r'([</(].*?[/)>]-?)')

for directory in os.listdir(root_dir):
    sub_dir = os.path.join(root_dir, directory)
    if not os.path.isdir(sub_dir):
        continue
    for file in os.listdir(sub_dir):
        if not file.endswith('.TextGrid'):
            continue
        print(file)
        tg_path = os.path.join(sub_dir, file)
        tg = openTextgrid(tg_path, includeEmptyIntervals=False)

        for tier_name in tg.tierNameList:
            intervals = []
            tier = tg.tierDict[tier_name]
            for interval in tier.entryList:
                label = interval.label
                if label.startswith('/not'):
                    label = label[1:]
                if label.endswith('/RD-NAME-2'):
                    label += '/'
                elif label == '/RD-NAME-4':
                    label = '/RD-NAME-4/'
                elif label == 'RD-WORK-4,':
                    label = '/RD-WORK-4/'
                for k,v in replacements.items():
                    label = label.replace(k, v)
                #if '/- ' in label:
                #    print(label)
                    #error
                for m in bracket_pattern.finditer(label):
                    #print(m)
                    text = m.groups()[0]
                    replacement =  text.replace('/', '_').replace(' ', '_')
                    label = label.replace(text, replacement)
                for m in slash_pattern.finditer(label):
                    #print(m)
                    text = m.groups()[0]
                    replacement = text[1:-1]
                    if replacement.endswith('/'):
                        replacement = replacement[:-1]
                    replacement = '['+ replacement + ']'
                    label = label.replace(text, replacement)
                if label.endswith('.'):
                    label = label[:-1]
                if  not label:
                    continue
                print(label)
                intervals.append(Interval(interval.start, interval.end, label))
            new_tier = IntervalTier(maxT=tier.maxTimestamp,
                                    minT=tier.minTimestamp,
                                    name = tier.name,
                                    entryList=intervals)
            tg.replaceTier(tier.name, new_tier)
            print(tier_name)
        print(tg_path)
        print(tg)
        tg.save(tg_path, format='short_textgrid', includeBlankSpaces=True)