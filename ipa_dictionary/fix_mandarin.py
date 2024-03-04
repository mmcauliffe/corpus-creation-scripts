# coding=utf8
import os
import re
import itertools
from collections import Counter

gp_ja_dir = r'D:\Data\speech\GlobalPhone\trl'
working_dir = r'/mnt/d/Data/speech/GlobalPhone/mandarin/trl'
output_dir = r'/mnt/d/Data/speech/GlobalPhone/mandarin/labs'
lab_dir = r'D:\Data\speech\GlobalPhone\mandarin'

def num2chinese(num, big=False, simp=True, o=False, twoalt=False):
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used,
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
    revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and unit[1] == '0':
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)

pronunciations = {}

bad_chars = {'，', '。', '、', '「', '」','・・・',  '。', '：', ' ', '-','--', '──', '─', '）', '（', '――', '───', '……',
             '_', '－', '＆', '・', '＋', ';', '<', '〈', '〉', '-', '>', '“', '”', '―', '／', '─', '…', '！', '　', '『', '』', '；', '’', '‘', '（', '）', '《', '》', '？','(', ')'}
digit_mapping = {
    '２６．４２': '二十六点四十二',
    '１９９６１９９６': '十九九十六十九九六',
    '５００５１３３': '五〇〇五一三三',
    '４４１００１１': '四四千一百十一',
    '４５００５１００': '四千五百五千一百',
    '１９１１９００': '一九十九一千九百',
    '４５７４５７': '四百五十七四百五十七',
    '１０８８００': '十八千八百',
    '２０９８６６': '二十万九千八百六十六',
    '１９９５９５': '十九九十五九十五',
    '２９５１５': '二十九五十五',
    '１３６１６３': '十三六十一六十三',
    '１５５９３': '一五十五九十三',
    '７１４９４': '七万千四百九十四',
    '７７６５７': '七万七千六百五十七',
    '９７３７４': '九万七千三百七十四',
    '１４９５７': '一万四千九百五十七',
    '２９２９５': '二万九千二百九十五',
    '２０２４５': '二十千二百四十五',
    '１５５４３': '一万五千五百四十三',
    '１５７８５': '一万五千七百八十五',
    '１４９５０': '一万四千九百五十',
    '４０１９３': '四万一百九十三',
    '４１０１１': '四十十一',
    '６０１１０': '六十一百十',
    '１１０４８': '一万一千四十八',
    '２２０００': '二万二千',
    '１７６００': '十七六百',
    '１９９９年': '十九九九年',
    '１９６６年': '十九六十六年',
    '１９６４年': '十九六十四年',
    '１９７８年': '十九七八年',
    '６．４': '六点四',
    '４．５': '四点五',
    '５３．５％': '五十三点五百分之',
    '８５１３': '八十五十三',
    '８０３７': '八十三十七',
    '９９５０': '九千九百五十',
    '９６９７': '九千六百九十七',
    '９３９２': '九千三百九十二',
    '９００１': '九千一',
    '９０００': '九千',
    '９２００': '九千二百',
    '９６００': '九千六百',
    '７３００': '七千三百',
    '５０００': '五千',
    '５７００': '五千七百',
    '５４００': '五千四百',
    '５２００': '五千二百',
    '５８８０': '五千八百八十',
    '５８２０': '五千八百二十',
    '８０００': '八千',
    '７０００': '七千',
    '７７００': '七千七百',
    '７５８０': '七千五百八十',
    '７４２３': '七千四百二十三',
    '６０００': '六千',
    '２０００': '二千',
    '２００５': '二千五',
    '３０００': '三千',
    '３２６８': '三千二百六十八',
    '４０００': '四千',
    '４０８０': '四千八十',
    '４０５５': '四千五十五',
    '１７００': '一千七百',
    '１４００': '一千四百',
    '１３００': '一千三百',
    '２１００': '二千一百',
    '２００７': '二千七',
    '２０８５': '二千八十五',
    '２３００': '二千三百',
    '２５００': '二千五百',
    '２６００': '二千六百',
    '２６６０': '二千六百六十',
    '４５００': '四千五百',
    '５５００': '五千五百',
    '５９７０': '五千九百七十',
    '５２３４': '五千二百三十四',
    '５７４８': '五千七百四十八',
    '２８００': '二千八百',
    '６８００': '六千八百',
    '６５００': '六千五百',
    '６４７４': '六十四七十四',
    '８８００': '八千八百',
    '４８００': '四千八百',
    '４８５７': '四千八百五十七',
    '４６００': '四千六百',
    '４４００': '四千四百',
    '４３００': '四千三百',
    '４９００': '四千九百',
    '４３０４': '四千三百四',
    '４３７５': '四千三百七十五',
    '４３８９': '四千三百八十九',
    '４３２６': '四千三百二十六',
    '４２１７': '四千二百十七',
    '４２６２': '四千二百六十二',
    '２５８５': '二千五百八十五',
    '２４５０': '二千四百五十',
    '２３７９': '二千三百七十九',
    '２９６１': '二千九百六十一',
    '２８５１': '二千八百五十一',
    '２４００': '二千四百',
    '３４００': '三千四百',
    '３１００': '三千一百',
    '３５００': '三千五百',
    '３２００': '三千二百',
    '２２００': '二千二百',
    '２７０２': '二千七百二',
    '２７００': '二千七百',
    '３８００': '三千八百',
    '３０３０': '三千三十',
    '３３５３': '三千三百五十三',
    '１９８０': '十九八〇',
    '１９９０': '十九九〇',
    '１９９１': '十九九一',
    '１８９１': '十八九一',
    '１９９２': '十九九二',
    '１９９５': '十九九五',
    '１９９８': '十九九八',
    '１９８９': '十九八九',
    '１９５８': '十九五十八',
    '１９５６': '十九五十六',
    '１９５５': '十九五十五',
    '１９５１': '十九五十一',
    '１９５７': '十九五十七',
    '１９８６': '十九八六',
    '１９８８': '十九八十八',
    '１９８７': '十九八七',
    '１９８２': '十九八二',
    '１９８３': '十九八三',
    '１９８４': '十九八四',
    '１９９７': '十九九七',
    '１９９６': '十九九六',
    '１９６６': '十九六六',
    '１９７９': '十九七九',
    '１９５９': '十九五十九',
    '１９４８': '十九四十八',
    '１９５０': '十九五十',
    '１９５２': '十九五十二',
    '１９２９': '十九２十九',
    '１９７６': '十九七六',
    '１９７２': '十九七二',
    '１９７０': '十九七〇',
    '１９７１': '十九七一',
    '１９９４': '十九九四',
    '１９９３': '十九九三',
    '１９６３': '十九六十三',
    '１９３８': '十九三十八',
    '１９３７': '十九三十七',
    '１９３２': '十九三十二',
    '１９３３': '十九三十三',
    '１９３４': '十九三十四',
    '１９３１': '十九三十一',
    '１９６７': '十九六十七',
    '１９１９': '十九十九',
    '１２００': '一千二百',
    '１１５０': '一千一百五十',
    '１１６８': '一千一百六十八',
    '１９００': '一千九百',
    '１２７７': '一千二百七十七',
    '１２５２': '一千二百五十二',
    '１２５１': '一千二百五十一',
    '１２８０': '一千二百八十',
    '１５００': '一千五百',
    '１４０３': '一千四百三',
    '１４１７': '一千四百十七',
    '１４１８': '一千四百十八',
    '１４９４': '一千四百九十四',
    '１５５４': '一千五百五十四',
    '１５２９': '一千五百二十九',
    '１８００': '一千八百',
    '１８７４': '一千八百七十四',
    '１８２０': '十八二十',
    '１８９２': '一千八百九十二',
    '１７５０': '一千七百五十',
    '１７３０': '十七三十',
    '１６００': '一千六百',
    '１６９０': '一千六百九十',
    '１６７６': '一千六百七十六',
    '１１７５': '一千一百七十五',
    '１０００': '一千',
    '１１００': '一千一百',
    '１１４０': '一千一百四十',
    '１１３０': '一千一百三十',
    '１０５０': '一千五十',
    '１０３８': '一千三十八',
    '１１３２': '一千一百三十二',
    '２００１': '二千一',
    '２００２': '二千二',
    '２００３': '二千三',
    '２０１０': '二千十',
    '１０２０': '一千二十',
    '２０２５': '二千二十五',
    '２０１０年': '二〇一〇年',
    '９８６': '九八十六',
    '５００': '五百',
    '５２０': '五百二十',
    '８００': '八百',
    '８０８': '八百八',
    '８４０': '八百四十',
    '８５０': '八百五十',
    '３５０': '三百五十',
    '３１５': '三百十五',
    '３４０': '三百四十',
    '３７０': '三百七十',
    '６７８': '六百七十八',
    '２７８': '二百七十八',
    '６００': '六百',
    '４００': '四百',
    '４０２': '四百二',
    '４２０': '四百二十',
    '４１０': '四百十',
    '４３０': '四百三十',
    '４５０': '四百五十',
    '６２０': '六百二十',
    '６５０': '六百五十',
    '６６９': '六百六十九',
    '６２８': '六百二十八',
    '８２０': '八百二十',
    '３０６': '三百六',
    '５１０': '五百十',
    '５９２': '五百九十二',
    '０５６': '〇五六',
    '５０７': '五百七',
    '２０７': '二百七',
    '３３３': '三百三十三',
    '３６６': '三百六十六',
    '３３０': '三百三十',
    '３０３': '三百三',
    '３８２': '三百八十二',
    '８３３': '八百三十三',
    '５６８': '五百六十八',
    '３６７': '三百六十七',
    '３６０': '三百六十',
    '２９２': '二百九十二',
    '２９６': '二百九十六',
    '２９０': '二百九十',
    '２６９': '二百六十九',
    '２６５': '二百六十五',
    '２２５': '二百二十五',
    '１６５': '一百六十五',
    '１６０': '一百六十',
    '１６４': '一百六十四',
    '１９５': '一百九十五',
    '１９３': '一百九十三',
    '１８３': '一百八十三',
    '１８７': '一百八十七',
    '１２３': '一百二十三',
    '１３２': '一百三十二',
    '１２５': '一百二十五',
    '２２６': '二百二十六',
    '９５９': '九百五十九',
    '９６４': '九百六十四',
    '９００': '九百',
    '９７０': '九百七十',
    '９４０': '九百四十',
    '７４０': '七百四十',
    '７３０': '七百三十',
    '３８６': '三百八十六',
    '３００': '三百',
    '２００': '二百',
    '２０２': '二百二',
    '２２０': '二百二十',
    '２６０': '二百六十',
    '４６２': '四百六十二',
    '４６１': '四百六十一',
    '３２１': '三百二十一',
    '３１２': '三百十二',
    '３２０': '三百二十',
    '３８０': '三百八十',
    '３０１': '三百一',
    '２３０': '二百三十',
    '２４０': '二百四十',
    '２５３': '二百五十三',
    '１００': '一百',
    '１１０': '一百十',
    '９１０': '九百十',
    '１０９': '一百九',
    '１０４': '一百四',
    '１２９': '一百二十九',
    '１２７': '一百二十七',
    '１１２': '一百十二',
    '１４７': '一百四十七',
    '１４９': '一百四十九',
    '１３６': '一百三十六',
    '１１９': '一百十九',
    '１０５': '一百五',
    '１５５': '一百五十五',
    '１５７': '一百五十七',
    '５５８': '五百五十八',
    '５２６': '五百二十六',
    '１０２': '一百二',
    '１０７': '一百七',
    '１１３': '一百十三',
    '１１７': '一百十七',
    '７００': '七百',
    '７８２': '七百八十二',
    '１７０': '一百七十',
    '１７２': '一百七十二',
    '１７８': '一百七十八',
    '７２７': '七百二十七',
    '１３０': '一百三十',
    '１３９': '一百三十九',
    '１５０': '一百五十',
    '１６１': '一百六十一',
    '１６３': '一百六十三',
    '４８０': '四百八十',
    '１８０': '一百八十',
    '１８８': '一百八十八',
    '１８５': '一百八十五',
    '１１８': '一百十八',
    '２５０': '二百五十',
    '１２８': '一百二十八',
    '１３８': '一百三十八',
    '１３３': '一百三十三',
    '１３１': '一百三十一',
    '１２２': '一百二十二',
    '１２０': '一百二十',
    '１２１': '一百二十一',
    '１７３': '一百七十三',
    '１７６': '一百七十六',
    '０７５': '〇七五',
    '７３１': '七百三十一',
    '１４２': '一百四十二',
    '２４２': '二百四十二',
    '２４５': '二百四十五',
    '２１２': '二百十二',
    '４２５': '四百二十五',
    '４３５': '四百三十五',
    '１９２': '一百九十二',
    '１９０': '一百九十',
    '２７１': '二百七十一',
    '２８１': '二百八十一',
    '３３８': '三百三十八',
    '２２８': '二百二十八',
    '２１８': '二百十八',
    '２０３': '二百三',
    '３０２': '三百二',
    '２８０': '二百八十',
    '２０８': '二百八',
    '７１': '七十一',
    '７４': '七十四',
    '５１': '五十一',
    '９１': '九十一',
    '５９': '五十九',
    '５４': '五十四',
    '９０': '九十',
    '９９': '九十九',
    '９８': '九十八',
    '９４': '九十四',
    '９２': '九十二',
    '１０': '十',
    '1０': '十',
    '１９': '十九',
    '１８': '十八',
    '１６': '十六',
    '１１': '十一',
    '２１': '二十一',
    '３１': '三十一',
    '４１': '四十一',
    '２５': '二十五',
    '２３': '二十三',
    '２８': '二十八',
    '３８': '三十八',
    '３４': '三十四',
    '３７': '三十七',
    '６７': '六十七',
    '２９': '二十九',
    '３５': '三十五',
    '３２': '三十二',
    '３６': '三十六',
    '３０': '三十',
    '７０': '七十',
    '７５': '七十五',
    '７２': '七十二',
    '６２': '六十二',
    '７６': '七十六',
    '７７': '七十七',
    '７９': '七十九',
    '６９': '六十九',
    '６３': '六十三',
    '８８': '八十八',
    '８７': '八十七',
    '８６': '八十六',
    '８４': '八十四',
    '８３': '八十三',
    '９７': '九十七',
    '７８': '七十八',
    '８０': '八十',
    '６０': '六十',
    '５０': '五十',
    '５６': '五十六',
    '５８': '五十八',
    '４０': '四十',
    '４４': '四十四',
    '４２': '四十二',
    '４８': '四十八',
    '４７': '四十七',
    '４３': '四十三',
    '４５': '四十五',
    '６５': '六十五',
    '６６': '六十六',
    '５５': '五十五',
    '５３': '五十三',
    '５２': '五十二',
    '４９': '四十九',
    '４６': '四十六',
    '２７': '二十七',
    '９６': '九十六',
    '２６': '二十六',
    '２４': '二十四',
    '１２': '十二',
    '１７': '十七',
    '１３': '十三',
    '２２': '二十二',
    '３９': '三十九',
    '３３': '三十三',
    '１４': '十四',
    '１５': '十五',
    '２０': '二十',
    '６１': '六十一',
    '６４': '六十四',
    '６８': '六十八',
    '８１': '八十一',
    '８２': '八十二',
    '８９': '八十九',
    '８５': '八十五',
    '９５': '九十五',
    '９３': '九十三',
    '５７': '五十七',
    '３': '三',
    '％': '百分之',
    '７': '七',
    '８': '八',
    '９': '九',
    '６': '六',
    '５': '五',
    '４': '四',
    '２': '二',
    '１': '一',
    '０': '〇',
    '．': '点',
    '.': '点',
}
counter = Counter()
def create_lab_files(texts):
    skip_files = {'131_101', '132_10', '131_10'}
    for k, v in texts.items():
        speaker_directory = os.path.join(output_dir,  k.split('_')[0])
        os.makedirs(speaker_directory, exist_ok=True)
        if not os.path.exists(os.path.join(lab_dir, f'CH{k}.lab')):
            continue
        if k in skip_files:
            continue
        with open(os.path.join(lab_dir, f'CH{k}.lab'), 'r', encoding='utf8') as f:
            pinyin_text = f.read().strip()
            new_words = []
            for w in pinyin_text.split():
                if w.startswith('bai3fen1zhi1'):
                    w = w.replace('bai3fen1zhi1', '') + ' bai3fen1zhi1'
                new_words.append(w)
            pinyin_text = ' '.join(new_words)
        speaker_id, utt_id = k.split('_')
        speaker_directory = os.path.join(output_dir, speaker_id)
        os.makedirs(speaker_directory, exist_ok=True)
        for punc in bad_chars:
            v = v.replace(punc, '')
        print(v)
        for r, c in digit_mapping.items():
            v = v.replace(r, c)
        counter.update(v)
        print(k)
        print(v)
        print(pinyin_text)
        char_ind = 0
        new_text = []
        words =pinyin_text.split()
        for w in words:
            num_chars = len(re.findall(r'\d', w))
            new_text.append(v[char_ind:char_ind+num_chars])
            char_ind += num_chars
        print(len(new_text), len(words))
        for i in range(len(new_text)):
            print(new_text[i], words[i])
            if re.search(r'[１２３４５６７８９０]', new_text[i]):
                error
        if len(re.findall(r'\d', pinyin_text)) != len(v):
            print(len(re.findall(r'\d', pinyin_text)), len(v))
            error
        sanitized = []
        for word in new_text:
            if not word:
                continue
            sanitized.append(word)
        lab_path = os.path.join(speaker_directory, f'CH{k}.lab')
        print(sanitized)
        with open(lab_path, 'w', encoding='utf8') as f:
            f.write(' '.join(sanitized))
    print(counter)

import spacy_pkuseg

seg = spacy_pkuseg.pkuseg(model_name='/mnt/c/Users/michael/Documents/Dev/Tools/3p_models/pkuseg/mixed')

possible_punctuation = set()

digit_mapping = {
    '１': '1',
    '２': '2',
    '３': '3',
    '４': '4',
    '５': '5',
    '６': '6',
    '７': '7',
    '８': '8',
    '９': '9',
    '０': '0'
}

digit_extract_pattern = re.compile(r"(?P<prefix>[^１２３４５６７８９０]*)(?P<number>[１２３４５６７８９０]+)(?P<separator>[．・.／]?)(?P<second_number>[１２３４５６７８９０]*) ?(?P<unit>[％‰钱桶许%亿个万分点时月代多日年份]*)")

fix_mappings = {
    '一九七九年': '１９７９年',
    '一九九七年': '１９９７年',
    '一九九二年': '１９９２年',
    '一九九六年': '１９９６年',
    '一九八○年': '１９８０年',
}

dash_pattern = re.compile(r'[-―－─](?=[１２３４５６７８９０])')
paren_pattern = re.compile(r'[（）]')

def convert_numbers(w):
    m = digit_extract_pattern.match(w)
    if any(x in w for x in digit_mapping):
        if m is None:
            print(w, words, ''.join(words))
            print(m, w)
            error
        prefix = m.group('prefix')
        number = m.group('number')
        separator = m.group('separator')
        second_number = m.group('second_number')
        unit = m.group('unit')
        print(f"PREFIX: {prefix}, NUMBER: {number}, SEP: {separator}, SECOND_NUMBER: {second_number}, UNIT: {unit}")
        if unit == '年' and len(number) == 4:
            new_number = [digit_mapping[x] for x in number]
            print(new_number, int(''.join(new_number)))
            if 2100 > int(''.join(new_number)) > 1000:
                for d in range(len(new_number)):
                    new_number[d] = num2chinese(int(new_number[d]), o=True)
                w = ' '.join(new_number) + ' ' + unit
                return w
        base = int(''.join(digit_mapping[x] for x in number))
        print(base)
        number = num2chinese(base)
        print(number)
        if second_number:
            second_number = num2chinese(int(''.join(digit_mapping[x] for x in second_number)))
        if separator == '／':
            separator = '分之'
            number, second_number = second_number, number
        elif separator in {'．', '.', '・'}:
            separator = '点'
        number = ' '.join(number)
        second_number = ' '.join(second_number)
        number_string = ' '.join(x for x in [number, separator, second_number] if x)
        print(number_string)
        if unit in {'％', '%', '‰'}:
            if prefix:
                prefix += ' '
            w = prefix + '百分之 '+ number_string
            w = ' '.join(seg.cut(w))
            return w
        w = ' '.join(x for x in [prefix, number_string, unit] if x)
        w = ' '.join(seg.cut(w))
    else:
        if '・' in w:
            w = w.replace('・', '')
        if '─' in w:
            print(w)
            error
    return w

def clean_up_texts(texts):
    for k, words in texts.items():
        new_words = []
        for i, w in enumerate(words):
            w = w.replace('--', '')
            if any(x in w for x in digit_mapping) and dash_pattern.search(w):
                ws = dash_pattern.split(w)
                ws.insert(1, '到')
                if len(ws) > 3:
                    print(words[i], w, ws)
                    error
            elif dash_pattern.search(w):
                ws = dash_pattern.split(w)
            elif '（' in w:
                ws = paren_pattern.split(w)
            else:
                ws = [w]
            for w in ws:
                w = convert_numbers(w)
                new_words.append(w)

        if words != new_words:
            print("ORIGINAL:", words)
            print("MODIFIED:", new_words)
        texts[k] = new_words
    return texts

replacements = {
    ("CH019", 18): ('─４４', '到４４'),
    ("CH019", 26): ('１-０', '１到０'),
    ("CH029", 2): ('１─１', '１到１'),
    ("CH029", 3): ('１─１', '１到１'),
    ("CH029", 9): ('１─１', '１到１'),
    ("CH029", 14): ('１─１', '１到１'),
    ("CH031", 13): ('―１', '到１'),
    ("CH031", 31): ('－２', '到２'),
    ("CH038", 6): ('－１', '到１'),
    ("CH070", 68): ('─', '到'),
    ("CH070", 88): ('─', '到'),
    ("CH072", 33): ('―', '到'),
    ("CH074", 74): ('─', '到'),
    ("CH075", 7): ('─', '到'),
    ("CH075", 9): ('─', '到'),
    ("CH076", 83): ('─', '到'),
    ("CH079", 51): ('─', '到'),
    ("CH086", 6): ('─', '到'),
    ("CH086", 55): ('─', '到'),
    ("CH094", 105): ('─', '到'),
    ("CH104", 24): ('─', '到'),
    ("CH104", 26): ('─', '到'),
    ("CH105", 59): ('─', '到'),
    ("CH107", 72): ('─', '到'),
    ("CH107", 73): ('─', '到'),
    ("CH107", 74): ('─', '到'),
    ("CH109", 37): ('─', '到'),
    ("CH109", 44): ('─', '到'),
    ("CH109", 47): ('─', '到'),
    ("CH109", 51): ('─', '到'),
    ("CH109", 53): ('─', '到'),
    ("CH109", 57): ('─', '到'),
    ("CH113", 78): ('─', '到'),
    ("CH114", 77): ('─', '到'),
    ("CH117", 59): ('─', '到'),
    ("CH120", 26): ('─', '到'),
    ("CH124", 2): ('─', '到'),
    ("CH127", 28): ('───', '到'),
    ("CH127", 49): ('───', ' '),
    ("CH128", 13): ('───', ' '),
    ("CH082", 60): ('<１９-１>', '<１９１->'),
    ("CH075", 12): ('───', ' '),
    ("CH075", 17): ('───', ' '),
    ("CH101", 3): ('─', ' '),
    ("CH101", 9): ('─', ' '),
    ("CH105", 51): ('─', ' '),
    ("CH108", 6): ('───', ' '),
    ("CH110", 63): ('───', ' '),
    ("CH111", 70): ('─', ' '),
    ("CH113", 92): ('─', ' '),
    ("CH115", 20): ('─', ' '),
    ("CH115", 21): ('─', ' '),
    ("CH115", 23): ('─', ' '),
    ("CH115", 26): ('─', ' '),
    ("CH115", 41): ('─', ' '),
    ("CH116", 57): ('───', ' '),
    ("CH113", 97): ('─', ' '),
    ("CH113", 100): ('─', ' '),
    ("CH105", 52): ('─', ' '),
    ("CH105", 63): ('─', ' '),
    ("CH105", 71): ('─', ' '),
    ("CH102", 57): ('───', ' '),
    ("CH075", 84): ('─', ' '),
    ("CH083", 66): ('─', ' '),
    ("CH083", 67): ('─', ' '),
    ("CH083", 70): ('─', ' '),
    ("CH083", 83): ('─', ' '),
    ("CH075", 85): ('─', ' '),
    ("CH075", 86): ('─', ' '),
    ("CH075", 88): ('─', ' '),
    ("CH075", 93): ('─', ' '),
    ("CH075", 94): ('─', ' '),
    ("CH093", 29): ('─', ' '),
    ("CH093", 52): ('─', ' '),
    ("CH093", 60): ('───', ' '),
    ("CH093", 61): ('───', ' '),
    ("CH028", 98): ('───', '，'),
    ("CH045", 12): ('───', '，'),
    ("CH049", 60): ('鲁─', '鲁 '),
    ("CH050", 74): ('鲁─', '鲁 '),
    ("CH050", 86): ('─１', '到１'),
    ("CH051", 41): ('-', ' '),
    ("CH052", 88): ('───', ' '),
    ("CH059", 107): ('─', ' '),
    ("CH059", 108): ('─', ' '),
    ("CH064", 1): ('──', ' '),
    ("CH062", 29): ('───', ''),
    ("CH074", 28): ('───', ''),
    ("CH074", 30): ('───', ''),
    ("CH073", 30): ('─', ''),
    ("CH073", 31): ('─', ''),
    ("CH120", 50): ('───', ''),
    ("CH066", 71): ('―', ' '),
    ("CH066", 81): ('―', ' '),
    ("CH063", 85): ('Ｆ─', 'Ｆ '),
    ("CH092", 8): ('Ｆ─', 'Ｆ '),
}

if __name__ == '__main__':
    bracket_pattern = re.compile(r'[<(（].*?[）)>]')
    for file in os.listdir(working_dir):
        speaker_id = os.path.splitext(file)[0]
        path = os.path.join(working_dir, file)
        texts = {}
        current_utterance = 0
        with open(path, 'r', encoding='gb2312') as f:
            for line in f:
                if 'SprecherID' in line:
                    continue
                if line.startswith(';'):
                    current_utterance += 1
                    continue
                else:
                    line = line.strip()
                    if not line:
                        continue
                    start_ind = 0
                    line = line.replace('―――','，')
                    line = line.replace('───。','。')
                    line = line.replace('；───','；')
                    line = line.replace('：───','：')
                    line = line.replace('”───','”')
                    line = line.replace('？───','？')
                    line = line.replace('───<','<')
                    line = line.replace('斯－伯','斯 伯')
                    line = line.replace('道―琼','道 琼')
                    if (speaker_id, current_utterance) in replacements:
                        r = replacements[(speaker_id, current_utterance)]
                        line = line.replace(*r)
                    segs = []
                    for m in bracket_pattern.finditer(line):
                        segs.append(line[start_ind:m.start(0)])
                        word = m.group(0).replace(')', '>').replace('）', '>').replace('(', '<').replace('（', '<').replace(' ', '')
                        print(m, word)
                        segs.append(word)
                        start_ind=m.end(0)
                    if line[start_ind:]:
                        segs.append(line[start_ind:])
                    words = []
                    for segment in segs:
                        if bracket_pattern.match(segment):
                            words.append(segment)
                            continue
                        words.extend(x for x in seg.cut(segment) if x not in bad_chars)

                    print(speaker_id, current_utterance)
                    print("ORIGINAL", line)
                    for i, w in enumerate(words):
                        if bracket_pattern.match(w):
                            continue
                        words[i] = convert_numbers(w)
                    print("OUTPUT", words)
                    #print(line)
                    #print(text)
                    if '―――' in line:
                        error
                    if dash_pattern.search(line):
                        error
                    #if (speaker_id, current_utterance) == ('CH073', 74):
                    #    error
                    possible_punctuation.update([w for w in words if len(w) == 1])
                    if current_utterance not in texts:
                        texts[current_utterance] = words
                    else:
                        texts[current_utterance] += words
        speaker_output_dir = os.path.join(output_dir,speaker_id)
        os.makedirs(speaker_output_dir, exist_ok=True)
        for utt, text in texts.items():
            lab_path = os.path.join(speaker_output_dir,  f"{speaker_id}_{utt}.lab")
            with open(lab_path, 'w', encoding='utf8') as f:
                f.write(' '.join(text))
    #print(sorted(possible_punctuation))
    error
    create_lab_files(all_texts)