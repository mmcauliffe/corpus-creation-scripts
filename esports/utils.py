import os
import textgrid
import webvtt
import datetime

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_api_key():
    with open(os.path.join(root_dir, 'api_key'), 'r') as f:
        return f.read().strip()

key = load_api_key()


def analyze_subtitles(path):
    tg_path = path.replace('.en.vtt', '.TextGrid')
    tg = textgrid.TextGrid()
    speech_tier = textgrid.IntervalTier(name='speech')
    prev_caption = []
    for caption in webvtt.read(path):
        print(caption.start)
        date_time = datetime.datetime.strptime(caption.start, '%H:%M:%S.%f')
        delta = date_time - datetime.datetime(1900, 1, 1)
        start = delta.total_seconds()
        print(start)
        print(caption.end)
        date_time = datetime.datetime.strptime(caption.end, '%H:%M:%S.%f')
        delta = date_time - datetime.datetime(1900, 1, 1)
        end = delta.total_seconds()
        print(end)
        lines = caption.text.strip().splitlines()
        lines = [x.strip() for x in lines]
        actual_lines = [x for x in lines if x not in prev_caption]
        if not actual_lines:
            continue
        print(actual_lines)
        speech_tier.add(start, end, actual_lines[0])
        prev_caption = lines
    tg.append(speech_tier)
    tg.write(tg_path)
    os.remove(path)


def check_exists_other(audio_path, other_places):
    for d in other_places:
        if os.path.exists(os.path.join(d, audio_path)):
            return True
    return False