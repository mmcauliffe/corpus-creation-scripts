import os
import subprocess
import requests
import re
import sys
esports_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, esports_dir)
from utils import key, check_exists_other, analyze_subtitles

data_directory_pattern = r'D:\Data\speech\esports\overwatch\{}\owl'
raw_data_directory = data_directory_pattern.format('raw')

other_places = [data_directory_pattern.format(x) for x in ['cleaned', 'segmented', 'to_transcribe', 'transcribed', 'finalized']]
os.makedirs(raw_data_directory, exist_ok=True)


channel_id = 'UC38VAZEq3chAIPf4i2AIq7Q'

playlist_ids = [
    'PLwnBEhITAFhhJPLEj-XcJBAgM_yMaQpKs',
    'PLwnBEhITAFhh3LmI-iJQnBYQ5xdHisGEB',
    'PLwnBEhITAFhjG0ARWNDM_dYSZlbtJzS3Y',
    'PLwnBEhITAFhga7oi_Tjcf-Tm9W290LD1e',
]

playlist_names = {
 'PLwnBEhITAFhhJPLEj-XcJBAgM_yMaQpKs': 'OWL 2018',
    'PLwnBEhITAFhh3LmI-iJQnBYQ5xdHisGEB': 'OWL 2019',
    'PLwnBEhITAFhjG0ARWNDM_dYSZlbtJzS3Y': 'OWL 2020',
    'PLwnBEhITAFhga7oi_Tjcf-Tm9W290LD1e': 'OWL 2021',
}




def download_audios():
    for playlist_id in playlist_ids:
        cursor = None
        while True:
            if not cursor:
                url = 'https://www.googleapis.com/youtube/v3/playlistItems?key={}&playlistId={}&part=snippet,id&order=date&maxResults=50'.format(
                    key, playlist_id)
            else:
                url = 'https://www.googleapis.com/youtube/v3/playlistItems?key={}&playlistId={}&part=snippet,id&order=date&maxResults=50&pageToken={}'.format(
                    key, playlist_id, cursor)
            response = requests.get(url)
            data = response.json()
            if 'error' in data:

                print(data)
                break
            for item in data['items']:
                try:
                    v_id = item['snippet']['resourceId']['videoId']
                except KeyError:
                    continue
                url = 'https://www.youtube.com/watch?v=' + v_id
                if item['snippet']['title'].lower().startswith('overwatch league 2021'):
                    continue
                d = item['snippet']['publishedAt'].split('T')[0]
                title = re.sub(r'[^-\w _]', '', item['snippet']['title'])
                new_id = '{} - {}'.format(playlist_names[playlist_id], title).replace('|', '-').replace(' ', '_')
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
                    if os.path.exists(video_path):
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