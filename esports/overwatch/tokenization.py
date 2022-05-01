import os
import re
from num2words import num2words

base_dir = r'D:\Data\speech\esports\overwatch_texts'

output_dir = r'D:\Data\speech\esports\overwatch_tokenized'

os.makedirs(output_dir, exist_ok=True)

texts = os.listdir(base_dir)

months = ['january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr', 'may', 'june', 'jun', 'july', 'jul',
          'august', 'aug', 'september', 'sept', 'october', 'oct', 'november', 'nov', 'december', 'dec']

replacements = {
    'Dec.': 'december',
    'Dec ': 'december ',
    'Nov.': 'november',
    'Nov ': 'november ',
    'Oct.': 'october',
    'Oct ': 'october ',
    'Sept.': 'september',
    'Sept ': 'september ',
    'Aug.': 'august',
    'Aug ': 'august ',
    'Jul.': 'july',
    'Jul ': 'july ',
    'Jun.': 'june',
    'Jun ': 'june ',
    'Apr.': 'april',
    'Apr ': 'april ',
    'Mar.': 'march',
    'Mar ': 'march ',
    'Feb.': 'february',
    'Feb ': 'february ',
    'Jan.': 'january',
    'Jan ': 'january ',
    'D.Va': 'Dva',
    'i.e.': 'ie',
    'I.e.': 'ie',
    'etc.': 'etc',
    ' ': ' ', '，': ',',
    'GMT+': 'GMT +',
    'x2.5': '2.5x',
    'x2': '2x',
    '6 + 1': 'six plus one',
    '6 plus 1': 'six plus one',
    'Symmera': 'Symmetra','Symmeta': 'Symmetra',
    '#OWL2019': '', '#OWL2020': '', '#OWL2021': '', '#OWL2018': '',
    ".’": '', '-midnight': ' to midnight', 'p.m.PDT': 'p.m. PDT',
    '.”': '', ':–': ':', '%–': '%', '~$': 'about $', 'th-': 'th ', ']': '', '[': '', '🕢': '', '🧡': '', '®': '',
    '’': "'", '‘': "'", "”": '', '“': '', '"': '', '(': '', ')': '', ': ': ' ', ';': '', ',': '', '—': ' ', '?—?': ' ',
    '&': ' and ',
    '→': '', '🏂': '', '🤭': '', '👏': '', '➡': '', '⏰': '', '🏆': '', '👀': '', '😈': '', '🌄': '', '🙌': '', '🎁': '',
    '📺': '',
    '🥇': '', '😘': '', '🐙': '', '😊': '', '🔴': '', '😍': '', '🤩': '', '🤯': '', '😎': '', '🔨': '', '✅': '',
    '😮': '',
    '🐒': '', '👉': '', '👊': '', '🛒': '', '👽': '', '🛸': '', '🏃‍♀': '', '⚽': '', '🏠': '', '🪓': '', '🚨': '',
    '🤣': '', '😲': '', '😉': '', '🎆': '',
    '!#': '! #', '?#': '? #',
    'rate/win%': 'rate per win percent', 'T/': 'T '}

year_transforms = {
    '2020': 'twenty twenty',
    '2021': 'twenty twenty-one',
    '2022': 'twenty twenty-two',
    '2019': 'twenty nineteen',
    '2018': 'twenty eighteen',
    '2017': 'twenty seventeen',
    '2017s': 'twenty seventeen\'s',
    '2016': 'twenty sixteen',
    '2015': 'twenty fifteen',
    '2014': 'twenty fourteen',
    '1850s': 'eighteen fifties',
    '1950s': 'nineteen fifties',
    '1950s-style': 'nineteen fifties style',
    '50s-style': 'fifties style',
    '1960s': 'nineteen sixties',
    '1970s': 'nineteen seventies',
    '1980s': 'nineteen eighties',
    '1980s-themed': 'nineteen eighties themed',
    '1990s': 'nineteen nineties',
    '2000s': 'two thousands',
    '2000s-era': 'two thousands era',
    '20s': 'twenties',
    '2s': 'two\'s',
    '70s': 'seventies',
    "'70s": 'seventies',
    "'60s": 'sixties',
    "'80s": 'eighties',
    "'90s": 'nineties',
    "'21": 'twenty twenty-one',
    '1v1': 'one v. one',
    '1:1': 'one v. one',
    '5v6': 'five v. six',
    "1v1's": 'one v. ones',
    "+1": 'plus one',
}

team_transforms = {
    'O2': 'o. two',
    'M8': 'm. eight',
    'OW1\'s': 'o. w. one\'s',
    'OW1': 'o. w. one',
    'OW2': 'o. w. two',
    'ow2': 'o. w. two',
    'Ow2': 'o. w. two',
    '2CP': 'two c. p.',
    'Over.gg': 'over dot g. g.',
    'G2': 'g. two',
    'H2': 'h. two',
    'XL2': 'x. l. two',
    'XL2\'s': 'x. l. two\'s',
    'ATL': 'atlanta',
    'T1': 't. one',
    'T6': 't. six',
    'T6\'s': 't. six\'s',
    'T1W': 't. one w.',
    'T1W.GZA': 't. one w. dot g. z. a.',
    'T1w.GZA': 't. one w. dot g. z. a.',
    'T1w': 't. one w.',
    'H1Z1': 'h. one z. one',
    "T1's": "t. one's",
    'T2': 't. two',
    'T3': 't. three',
    'F1': 'f. one',
    'F5': 'f. five',
    'E3': 'e. three',
    'Formula1': 'formula one',
    'S2': 'season two',
    'SC2': 's. c. two',
    'TF2': 't. f. two',
    'TF2‘s': 't. f. two\'s',
    'TF2\'s': 't. f. two\'s',
    '3D': 'three d.',
    'PS4': 'p. s. four',
    'PlayStation4': 'playstation four',
    'PS5': 'p. s. five',
    'ESPN2': 'e. s. p. n. two',
    'ESPN3': 'e. s. p. n. three',
    '2D': 'two d.',
    '2‘s': 'two\'s',
    'Dust2': 'dust two',
    '76ers': 'seventy sixers',
    '7Lions': 'seven lions',
    "7Lions'": "seven lions's",
    'X6': 'x. six',
    'X2': 'x. two',
    '5G': 'five g.',
    "0'd": "oh'd",
    "0'ing": "oh'ing",
    "1'ing": "one'ing",
    "0'ed": "oh'd",
    "Soldier:76": 'soldier seventy six',
    "Solider:76": 'soldier seventy six',
    "soldier:76": 'soldier seventy six',
    "SOLDIER:76": 'soldier seventy six',
    "Soldier76": 'soldier seventy six',
    "Reaper76": 'reaper seventy six',
    "X6's": "x. six's",
    'Arc6': 'arc six',
    'Cloud9': 'cloud nine',
    "Cloud9's": "cloud nine's",
    "Cloud9s": "cloud nine's",
    'Sport1': 'sport one',
    'eSports1': 'esports one',
    'C9': 'c. nine',
    'Z9': 'z. nine',
    'S6': 's. six',
    'v1': 'v. one',
    'v2': 'v. two',
    'v3': 'v. three',
    'C9s': 'c. nine\'s',
    'C9\'s': 'c. nine\'s',
    'Sig9': 'sig nine',
    'OR15': 'o. r. fifteen',
    "OR15's": 'o. r. fifteens',
    'OR14s': 'o. r. fourteens',
    'OR15s': 'o. r. fifteens',
    'Bo5': 'best of five',
    'Bo3': 'best of three',
    'Bo7': 'best of seven',
    'Day9': 'day nine',
    'Go4Cup': 'go four cup',
    'COVID19': 'covid nineteen',
    'i7': 'i. seven',
    'i52': 'i. fifty two',
    'i49': 'i. forty nine',
    'DOTA2': 'dota two',
    'map3': 'map three',
    'XM4': 'x. m. four',
    '5mW': 'five mega watt',
    'M16': 'm. sixteen',
}

removals = {
    'Champion2020', 'wins.3', 'MSI GTX', 'Workshop Code', '8BitPink', 'workshop code', 'August8', 'Z5XK2',
    'Workshop code', '1XSGZ', "Workshop's", 'Contact the author',
    '4QY7Z', 'PC419', '1FS', '~2.13', 'PS3P4', 'Gaming2', 'Immortals3', 'Gaming4', '\'12', 'cc.163', '2o20', '6+1',
    '3.0x', 'VZ4YG', '3ds', '15°', 'China.7', 'season.6', 'Karahe',
    '💉', '″', '×', '🌙', '😋', '🙄', '오', '😀', '🖤', '1⃣', '📂', '년', '여', '이', '통', '통', '🙂', '.com', '😏', 'No.1',
    '연', '3DS', '》', '名', '🛡️', '⚔', '👑', '🔫', '🇭🇰', '🇷🇺', '日', 'た',
    '다', '다', '𝗡', '1Equip', 'M4A1',
    '|￣￣￣￣￣￣￣￣￣￣￣|',
    'ça',
    'ó﹏ò｡',
    '̫',
    'ΛNNIE',
    'οκτωβρίου',
    'π',
    'Σ',
    'в',
    'вылетаем',
    'голландии',
    'забираем',
    'и', 'ô',
    'из',
    'карту',
    'матче',
    'мы',
    'престижа',
    'сборной',
    'со',
    'турнира',
    'ѣѻү',
    'ԍѻѻԁ',
    '•̀',
    '•́',
    '•◡•',
    '‪',
    '™',
    '∑',
    '∑d°∀°d',
    '≠', 'très', 'tiipiö',
    '⋜',
    "◝'ω'◝", 'ѻ', 'ү', 'σ', 'β', 'λ',
                                 "◟'ω'◟", '❤️', '❗️', '🧩', '🧚',
    '✧', '📣', '🗸', 'Ä', '💙', '📆', '🎊', '@', '*', '🔥', '⚡', '탈', '#', '🥣', 'و', 'ي'
}

longs = ['waitwaitwaiiiiiiiiiiiiiiiiiiiittttttttttttttttttttttttttttt'.upper(), 'preeeeetty', 'torbrbrbrbbrbrbrbrbrbrbbrbrbrbrbrbrbrbrb',
         'gogogogogogogowe', 'goooooaaaaaaallls', 'goooooooooo','wrgoababdmliaoiwtbimpanetpmliaboaiaqcittmtsamstgab',]

removals.update(
    '🦊🦁🦀🥳🥳🥰🤷🤠🤝🤘🤖🤓🚀🙏😻😳😱😭😤😢😡😛😌😇😆😁🖊🕹🕸🕶🔮🔎🔊📰📡📝📈📅💻💫💪💥💎💃💀👻👌👋👁🐼🎉🐸🐲🐯🐧🐓🐐🐅🏿🏮🏖🏎🏊🏊🎺🎵🎯🎮🎭🎨🎧🎤🎣🎟🎖🎎🎍🌉🇺🇸🇳🇱🇰🇮🇫🇪🇩🇨🇧🇦𝙀𝗳𝗪𝗝𝗛𝗙𝗕𝐶했트쪼스소박뭐관간海杭新休⩲❤❗✨❄✌⛸⛄⚖⚓')
removals.update('♻☆☃☁☀🐺🐹🐷🐱🎃🍦🍕🍁🌵🌲🌧🌊♥💍💚📢✊리🔔🙁👇ᆯ🇹🇼♡🌩🎶🏯🐀🐈🐰📷📸🔓😼🛑🛡🛡🤔🧟≦︶∀🌟！💣')


def sanitize(sentence):
    for k, v in replacements.items():
        sentence = sentence.replace(k, v)
    sentence = re.sub(r'(\d)[-—–]', r'\1 ', sentence)
    sentence = re.sub(r'[-—–](\d)', r' \1', sentence)
    sentence = re.sub(r'(\d)[/]', r'\1 per ', sentence)
    sentence = re.sub(r'(\d)[!]', r'\1 ', sentence)
    sentence = re.sub(r'(?<=\d) ([paPA])\.? ?[mM]\.?\b', r'\1.m.', sentence)
    if 'https' not in sentence and '.com' not in sentence:
        sentence = re.sub(r'(?<=\w)/', r' ', sentence)
    if sentence.endswith('.'):
        sentence = sentence[:-1]
    return sentence


tokenized_sentences = []

for t in texts:
    if t.endswith('links.txt'):
        continue
    print(t)
    with open(os.path.join(base_dir, t), 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = sanitize(line)
            if 'https' in line:
                continue
            # print(line)
            sentences = re.split(r'((?<!St)(?<!a.m)(?<!a .m)(?<!p.m)(?<!p .m)[.] |[!?…][\'"]?\s?|[.][.][.] ?|[.](?=[A-Z][a-z]))',
                                 line)
            # print(sentences)
            for s in sentences:
                # print(s)
                s = s.split()
                for i, word in enumerate(s):
                    word = re.sub(r'(?<!\d)[,.!?";:)…‘]+(?!\w)', '', word)
                    word = re.sub(r'[:]$', '', word)
                    word = re.sub(r'(\d)\'$', r'\1', word)
                    word = re.sub(r'^(\d)(\d\d)([pa]m)$', r'\1:\2\3', word)
                    word = re.sub(r'^\'+', r'', word)
                    word = re.sub(r'([^s])\'$', r'\1', word)

                    word = word.replace('?', '')
                    word = word.strip()
                    # word = re.sub(r'[!?)]+\b', '', word)
                    s[i] = word
                    #print(word)
                    if not word:
                        continue
                    if word == ',':
                        s[i] = ''
                        continue
                    if word == "'":
                        s[i] = ''
                        continue
                    if word.startswith('https') or word.startswith('pic.') or word.startswith('pictwitter'):
                        s[i] = ''
                        continue
                    if word.startswith('@'):
                        s[i] = ''
                        continue
                    elif word == '$HUYA' or re.match(r'^#[a-zA-Z]', word):
                        s[i] = ''
                        continue
                    if word in year_transforms:
                        s[i] = year_transforms[word]
                    elif word in team_transforms:
                        s[i] = team_transforms[word]
                    elif re.match(r'^(\$|AU\$|€|¥|£)', word) or re.search(r'(\$|AU\$|€|¥|£|EUR)$', word):
                        if word.startswith('$AU') or word.startswith('AU$'):
                            dollar_phrase = 'dollars australian'
                            word = word[3:]
                        elif word.endswith('$'):
                            dollar_phrase = 'dollars'
                            word = word[:-1]
                        elif word.startswith('€'):
                            dollar_phrase = 'euros'
                            word = word[1:]
                        elif word.endswith('EUR'):
                            dollar_phrase = 'euros'
                            word = word[:-3]
                        elif word.endswith('¥'):
                            dollar_phrase = 'yuan'
                            word = word[:-1]
                        elif word.startswith('¥'):
                            dollar_phrase = 'yuan'
                            word = word[1:]
                        elif word.startswith('£'):
                            dollar_phrase = 'pounds'
                            word = word[1:]
                        else:
                            dollar_phrase = 'dollars'
                            word = word[1:]
                        word = re.sub('[,.!?";)]', '', word)
                        if word.lower().endswith('k'):
                            word = word[:-1]
                            suffix = ' thousand ' + dollar_phrase
                        elif i != len(s) - 1 and s[i + 1] in ['million', 'thousand', 'billion']:
                            suffix = ''
                            s[i + 1] += ' ' + dollar_phrase
                        else:
                            suffix = ' ' + dollar_phrase
                        new_word = num2words(word)
                        new_word += suffix
                        s[i] = new_word.replace(',', '')
                    elif re.search(r'[+]?[%][+]?', word):
                        print('HELLO', word)
                        if word.endswith('+%'):
                            suffix = 'plus percent'
                            word = word[:-2]
                        elif word.endswith('%+'):
                            suffix = 'percent plus'
                            word = word[:-2]
                        else:
                            suffix = 'percent'
                            word = word[:-1]
                        if '.' in word:
                            nums = word.split('.')
                            if nums[0]:
                                new_word = num2words(nums[0]) + ' point '
                            else:
                                new_word = 'point '
                            for digit in nums[1]:
                                new_word += num2words(digit) + ' '
                        new_word = num2words(word)
                        new_word += ' ' + suffix
                        s[i] = new_word
                    elif re.match(r'^[\d,]+([hH][zpZP]|m[sm]?|[fF][pP][sS]|s|p|[Gg][bB])?$', word):
                        word = word.replace(',', '')
                        if word.lower().endswith('hz'):
                            word = word[:-2]
                            suffix = ' hertz'
                        elif word.lower().endswith('hp'):
                            word = word[:-2]
                            suffix = ' h. p.'
                        elif word.lower().endswith('gb'):
                            word = word[:-2]
                            suffix = ' g. b.'
                        elif word.lower().endswith('fps'):
                            word = word[:-3]
                            suffix = ' f. p. s.'
                        elif word.lower().endswith('mm'):
                            word = word[:-2]
                            suffix = ' millimeters'
                        elif word.lower().endswith('ms'):
                            word = word[:-2]
                            suffix = ' milliseconds'
                        elif word.lower().endswith('m'):
                            word = word[:-1]
                            suffix = ' meters'
                        elif word.lower().endswith('s'):
                            word = word[:-1]
                            suffix = ' seconds'
                        elif word.lower().endswith('p'):
                            word = word[:-1]
                            suffix = ' p.'
                        else:
                            suffix = ''
                        if i != 0 and s[i - 1].lower() in months:
                            new_word = num2words(word, to='ordinal')
                        else:
                            new_word = num2words(word)
                        s[i] = new_word.replace(',', '') + suffix
                    elif re.match(r'^\d+\.\d+(hz|[Kk]|s)?$', word):
                        if word.endswith('hz'):
                            word = word[:-2]
                            suffix = ' hertz'
                        elif word.lower().endswith('k'):
                            word = word[:-1]
                            suffix = ' k.'
                        elif word.lower().endswith('s'):
                            word = word[:-1]
                            suffix = ' seconds'
                        else:
                            suffix = ''
                        nums = word.split('.')
                        new_word = num2words(nums[0]) + ' point ' + num2words(nums[1])
                        s[i] = new_word + suffix
                    elif re.match(r'^\d+([Ss][tT]|[Rr][dD]|[Tt][Hh]|[Nn][dD])$', word):
                        new_word = num2words(word[:-2], to='ordinal')
                        s[i] = new_word
                    elif re.match(r"^\d?\d([:.]?\d\d)?([Aa]\.?[Mm]|[pP]\.?[mM])$", word):
                        if word.lower().endswith('am'):
                            suffix = ' a. m.'
                            word = word[:-2]
                        elif word.lower().endswith('pm'):
                            suffix = ' p. m.'
                            word = word[:-2]
                        elif word.lower().endswith('p.m'):
                            suffix = ' p. m.'
                            word = word[:-3]
                        elif word.lower().endswith('a.m'):
                            suffix = ' a. m.'
                            word = word[:-3]
                        else:
                            suffix = ''
                        if ':' in word:
                            nums = word.split(':')
                            new_word = num2words(nums[0]) + ' ' + num2words(nums[1]) + suffix
                        elif len(word) == 3:
                            if word[1:] != '00':
                                new_word = num2words(word[:1]) + ' ' + num2words(word[1:]) + suffix
                            else:
                                new_word = num2words(word[:1]) + suffix
                        elif len(word) == 4:
                            new_word = num2words(word[:2]) + ' ' + num2words(word[2:]) + suffix
                        else:
                            new_word = num2words(word) + suffix
                        s[i] = new_word
                    elif re.match(r'^\d\d:00$', word):
                        new_word = num2words(word.split(':')[0]) + ' hundred'
                        s[i] = new_word
                    elif re.match(r'^\d+:\d\d?$', word):
                        nums = word.split(':')
                        new_word = num2words(nums[0]) + ' ' + num2words(nums[1])
                        s[i] = new_word
                    elif re.match(r'^\d+[kK]$', word):
                        new_word = num2words(word[:-1]) + ' k.'
                        s[i] = new_word.replace(',', '')
                    elif re.match(r'^\d+[xX]$', word):
                        new_word = num2words(word[:-1]) + ' x.'
                        s[i] = new_word.replace(',', '')
                    elif re.match(r'^\.\d+$', word):
                        word = word[1:]
                        new_word = ' point'
                        for digit in word:
                            new_word += ' ' + num2words(digit)
                        s[i] = new_word
                    elif re.match(r'Q\d', word):
                        new_word = 'q. ' + num2words(word[1])
                        s[i] = new_word
                    elif re.match(r'^\d+\+$', word):
                        word = word[:-1]
                        new_word = num2words(word) + ' plus'
                        s[i] = new_word
                    elif re.match(r'^\+\d+$', word):
                        word = word[1:]
                        new_word = 'plus ' + num2words(word)
                        s[i] = new_word
                    elif re.match(r'^#\d+$', word):
                        word = word[1:]
                        new_word = 'number ' + num2words(word)
                        s[i] = new_word
                    elif re.match(r'^\d+v\d+$', word):
                        nums = word.split('v')
                        new_word = num2words(nums[0]) + ' v. ' + num2words(nums[1])
                        s[i] = new_word
                    elif re.match(r'^[17]\.\d\d?(\.\d)?(\.\d)?(\'s)?$', word):  # Patch versions
                        if word.endswith("'s"):
                            word = word[:-2]
                            suffix = "'s"
                        else:
                            suffix = ''
                        nums = [num2words(x) for x in word.split('.')]
                        s[i] = ' point '.join(nums) + suffix
                    elif re.match(r"^\d+'s$", word):
                        suffix = "'s"
                        word = word[:-2]
                        new_word = num2words(word) + suffix
                        s[i] = new_word
                    elif re.match(r'\w\+', word):
                        if word.endswith('+'):
                            word = word[:-1] + ' plus'
                        else:
                            word = ' plus '.join(word.split('+'))
                        s[i] = word
                    elif word.endswith('–'):
                        s[i] = word[:-1]
                    elif word.startswith('–'):
                        s[i] = word[1:]
                    elif word.startswith('^'):
                        s[i] = ''

                tokenized_sentences.append(' '.join(s))
                if re.search(r"^\"", tokenized_sentences[-1]) or "august9th" in tokenized_sentences[-1].lower():
                    print(tokenized_sentences[-1])
                    error

with open(os.path.join(output_dir, 'tokenized.txt'), 'w', encoding='utf8') as f:
    for s in tokenized_sentences:
        s = s.strip()
        if not s:
            continue
        if s.startswith('H/T'):
            continue
        if s.startswith('H T'):
            continue
        if any(x in s for x in removals):
            continue
        if any(x in s for x in longs):
            continue
        f.write(s + '\n')

print(removals)
print(longs)