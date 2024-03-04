# coding=utf8
import os
import re
import jaconv

gp_ja_dir = r'D:\Data\speech\GlobalPhone\Japanese\Japanese\trl'
working_dir = r'D:\Data\speech\GlobalPhone\Japanese\Japanese'
output_dir = r'D:\Data\speech\GlobalPhone\Japanese\Japanese\labs'


pronunciations = {}

def read_trl_file(path):
    speaker_id = None
    texts = {}
    current_utterance = 0
    with open(path, 'r', encoding='eucjp') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if speaker_id is None:
                speaker_id = line.strip().split()[1]
            elif re.match(r'^; \d+', line):
                current_utterance += 1
            elif re.match(r'^[;:/].*', line.strip()):
                continue
            else:
                print(current_utterance, line.strip())
                id = speaker_id + f'_{current_utterance}'
                if '一九九八年' in line:
                    line.replace('一九九八年', '千九九八年')
                if id not in texts:
                    texts[id] = line
                else:
                    texts[id] += ' ' + line
    print(speaker_id, current_utterance-1)
    return texts



katakana = ''.join(['ー','ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ', 'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ', 'ケ', 'ゲ', 'コ', 'ゴ', 'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ', 'タ', 'ダ', 'チ', 'ヂ', 'ッ', 'ツ', 'ヅ', 'テ', 'デ', 'ト', 'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'バ', 'パ', 'ヒ', 'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ヘ', 'ベ', 'ペ', 'ホ', 'ボ', 'ポ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ャ', 'ヤ', 'ュ', 'ユ', 'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ', 'ン', 'ヴ', 'ー'])
hiragana = ''.join(['ぁ', 'あ', 'ぃ', 'い', 'ぅ', 'う', 'え', 'ぉ', 'お', 'か', 'が', 'き', 'ぎ', 'く', 'ぐ', 'け', 'げ', 'こ', 'ご', 'さ', 'ざ', 'し', 'じ', 'す', 'ず', 'せ', 'ぜ', 'そ', 'ぞ', 'た', 'だ', 'ち', 'ぢ', 'っ', 'つ', 'づ', 'て', 'で', 'と', 'ど', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ば', 'ぱ', 'ひ', 'び', 'ぴ', 'ふ', 'ぶ', 'ぷ', 'へ', 'べ', 'ぺ', 'ほ', 'ぼ', 'ぽ', 'ま', 'み', 'む', 'め', 'も', 'ゃ', 'や', 'ゅ', 'ゆ', 'ょ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'ゎ', 'わ', 'を', 'ん'])
kanji_pattern = re.compile(rf'\{{?(?P<kanji>[\wＹＳＸＷＴＯＶＵＱＰＮＭＬＫＨＧ８ＦＤＣ＆ＢＡＲＩＥNAFTP&GICR]+)\[(?P<kana>\w+)\]\}}?')

kanas = set()
kanjis = set()

length_mappings = {
    'エイ': 'エー'
}

length_pattern = re.compile(r'((?<=[エェイィミシキチケニメリジビギネレヘヒテゲデベゼセペピ])イ|(?<=[タサマャラハパザガワダナカバアァ])[ア]|(?<=[ドノウムホオブプコズゾフォボユョヌルスグツヲロヨモトソュ])ウ(?![ィァェォュ]))')

def extract_kanji_pronunciations(text):
    for kanji, kana in kanji_pattern.findall(text):
        if '力のうりょく' in kana:
            print(text)
            print(kanji)
            print(kana)
            error
        if kana.startswith('UNK'):
            continue
        if re.match(rf'^[{katakana}]+$', kanji):
            while True:
                new_kanji =  length_pattern.sub('ー', kanji, 1)
                if new_kanji == kanji:
                    break
                kanji = new_kanji
            if kana == 'イアイイ' or kanji == 'イアイイ':
                print(kanji)
                print(kana)
                error
            kanas.add(kanji)
        else:
            if re.search(r'[ＹＳＸＷＴＯＶＵＱＰＮＭＬＫＨＧ８ＦＤＣ＆ＢＡＲＩＥNAFTP&GICR]+', kanji):
                kana = jaconv.hira2kata(kana)
                # Fix length
                while True:
                    new_kana =  length_pattern.sub('ー', kana, 1)
                    if new_kana == kana:
                        break
                    kana = new_kana
            if kana == 'エイティイアンドティイ' or kanji == 'エイティイアンドティイ':
                print(kanji)
                print(kana)
                error
            if kana == 'ー' or kanji == 'ー':
                print(kanji)
                print(kana)
                error
            kanas.add(kana)
            kanjis.add(kanji)

bad_characters = {'）', '（'}

def create_lab_files(texts):
    for k, v in texts.items():
        speaker_id, utt_id = k.split('_')
        speaker_directory = os.path.join(output_dir, speaker_id)
        os.makedirs(speaker_directory, exist_ok=True)
        text = v.replace('。', ' ').replace('、', ' ').replace('「', '').replace('」', '').replace('・・・', ' ')
        t = text.split()
        sanitized = []
        for word in t:
            if not word:
                continue
            if any(x in word for x in bad_characters):
                continue
            m = re.match(r'^\{?(?P<kanji>[-\w&＜×＞○＋＆―・％]+)\|?\[(?P<kana>.*)\]\}?$', word)
            if m:
                word = m.group('kanji')
                kana = m.group('kana')
            else:
                kana = None
            if word in {'’[UNK’]'}:
                continue
            if word in {'・', '％'} and sanitized:
                sanitized[-1] += word
                continue
            if  word.startswith('力の') or '[' in word or word.startswith('〇三'):
                print("BOOOOO")
                print(k)
                print(v)
                print(text)
                print(t)
                print(sanitized)
                error
            sanitized.append(word)
            if pronunciations and kana is not None:
                if re.match(rf'^[{katakana}]+$', word):
                    while True:
                        new_word =  length_pattern.sub('ー', word, 1)
                        if new_word == word:
                            break
                        word = new_word
                if re.search(r'[ＹＳＸＷＴＯＶＵＱＰＮＭＬＫＨＧ８ＦＤＣ＆ＢＡＲＩＥNAFTP&GICR]+', word):
                    kana = jaconv.hira2kata(kana)
                    # Fix length
                    while True:
                        new_kana =  length_pattern.sub('ー', kana, 1)
                        if new_kana == kana:
                            break
                        kana = new_kana
                if word not in pronunciations:
                    try:
                        pronunciations[word] = pronunciations[kana]
                    except KeyError:
                        pass
        lab_path = os.path.join(speaker_directory, f'JA{k}.lab')
        print(k, ' '.join(sanitized))
        for w in sanitized:
            if '＜' in w and not w.startswith('＜'):
                print(w)
                error
        if os.path.exists(lab_path):
            continue
        with open(lab_path, 'w', encoding='utf8') as f:
            f.write(' '.join(sanitized))


def save_kanas():
    with open(os.path.join(working_dir, 'to_g2p.txt'), 'w', encoding='utf8') as f:
        for k in sorted(kanas):
            f.write(f"{k}\n")

def save_pronunciations():
    with open(os.path.join(working_dir, 'ja_dict.txt'), 'w', encoding='utf8') as f:
        for k, v in sorted(pronunciations.items()):
            for v2 in sorted(v):
                f.write(f"{k}\t{v2}\n")


if __name__ == '__main__':
    if os.path.exists(os.path.join(working_dir, 'g2pped.txt')):
        with open(os.path.join(working_dir, 'g2pped.txt'), 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                line = line.split('\t')
                word = line[0]
                pron = line[1]
                if word not in pronunciations:
                    pronunciations[word] = set()
                pronunciations[word].add(pron)
    print(len(pronunciations))
    print(pronunciations['にちべい'])
    all_texts = {}
    for file in os.listdir(gp_ja_dir):
        if file == 'JA207.trl':
            print(file)
            for k, v in read_trl_file(os.path.join(gp_ja_dir, file)).items():
                print(k, v)
            #error
        #continue
        all_texts.update(read_trl_file(os.path.join(gp_ja_dir, file)))
    #error
    for u, t in all_texts.items():
        print(u)
        extract_kanji_pronunciations(t)
    print(len(kanas))
    print(len(kanjis))
    #save_kanas()
    create_lab_files(all_texts)
    #if os.path.exists(os.path.join(working_dir, 'g2pped.txt')):
    #    save_pronunciations()