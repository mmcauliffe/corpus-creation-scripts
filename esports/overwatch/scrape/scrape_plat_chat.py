import os
import subprocess
import requests
import re
import sys
esports_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, esports_dir)
from utils import key, check_exists_other, analyze_subtitles

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

data_directory_pattern = r'D:\Data\speech\esports\overwatch\{}\platchat'
raw_data_directory = data_directory_pattern.format('raw')

other_places = [data_directory_pattern.format(x) for x in ['cleaned', 'segmented', 'to_transcribe', 'transcribed', 'finalized']]

channel_id = 'UC38VAZEq3chAIPf4i2AIq7Q'

def download_audios():
    cursor = None
    while True:
        if not cursor:
            url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50'.format(
                key, channel_id)
        else:
            url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50&pageToken={}'.format(
                key, channel_id, cursor)
        response = requests.get(url)
        data = response.json()
        print(data)
        for item in data['items']:
            try:
                v_id = item['id']['videoId']
            except KeyError:
                continue
            url = 'https://www.youtube.com/watch?v=' + v_id

            d = item['snippet']['publishedAt'].split('T')[0]
            if '—' in item['snippet']['title']:
                parts = [x.strip() for x in item['snippet']['title'].split('—')]
                if (not parts[0].startswith('Plat') and parts[1].startswith('Plat'))\
                        or (not parts[0].startswith('Head') and parts[1].startswith('Head')):
                    parts[0], parts[1] = parts[1], parts[0]
                title = ' - '.join(parts)
            else:
                title = item['snippet']['title']
            title = re.sub(r'[^-\w _]', '', title)
            title = re.sub(r'\s+', ' ', title)
            new_id = '{}-{}'.format(d, title).replace(' ', '_')
            if 'Clutch_or_Kick' in new_id:
                continue
            out_template = '{}.%(ext)s'.format(new_id)
            audio_file = '{}.flac'.format(new_id)
            if check_exists_other(audio_file, other_places):
                continue
            audio_path = os.path.join(raw_data_directory, audio_file)
            if not os.path.exists(audio_path):
                video_path = os.path.join(raw_data_directory, '{}.m4a'.format(new_id))
                subprocess.call(['youtube-dl', "-f 140", '--write-auto-sub',
                                 '--sub-format', 'vtt', '--sub-lang', 'en',
                                 '-o', out_template,
                                 url, ], cwd=raw_data_directory)
                if not os.path.exists(video_path):
                    continue
                subprocess.call(['ffmpeg', '-i', video_path, '-vn', '-map_channel', '0.0.0', '-c:a', 'flac', '-sample_fmt', 's16', '-ar', '16000', audio_path])
                os.remove(video_path)
            vtt_path = os.path.join(raw_data_directory, '{}.en.vtt'.format(new_id))
            tg_path = vtt_path.replace('.en.vtt', '.TextGrid')
            if not os.path.exists(tg_path):
                if not os.path.exists(vtt_path):
                    subprocess.call(['youtube-dl', '--write-auto-sub',
                                     '--skip-download',
                                     '--sub-format', 'vtt', '--sub-lang', 'en',
                                     '-o', out_template,
                                     url, ], cwd=raw_data_directory)
                if os.path.exists(vtt_path):
                    analyze_subtitles(vtt_path)
        try:
            cursor = data['nextPageToken']
        except KeyError:
            break

if __name__ == '__main__':
    download_audios()