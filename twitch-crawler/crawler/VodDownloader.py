import requests
import re
import os
import shutil
import subprocess
from multiprocessing.pool import ThreadPool

ACCESS_TOKEN_URL = "https://api.twitch.tv/api/vods/%s/access_token"
VIDEO_SOURCE_URL = "https://usher.ttvnw.net/vod/%s.m3u8?nauthsig=%s&nauth=%s&allow_source=true&player=twitchweb&allow_spectre=true&allow_audio_only=true"

video_options = [
    '160p30',
    '360p30',
    '480p30',
    '720p30',
    '720p60',
    'audio_only',
    'chunked'
]

NUMBER_OF_THREADS = 10

def extract_parts(data, url):
    lines = data.split("\n")
    url_splited = url.split('/')
    url = '/'.join(url_splited[:-1]) + '/'
    i = 0
    result = []
    while i < len(lines):
        if lines[i][:7] == '#EXTINF':
            result.append(url + lines[i + 1])
        i += 1
    return result

class VodDownloader:
    def __init__(self, client_id, out_dir = 'dist', number_of_threads = 10):
        self.base_url = 'https://api.twitch.tv/helix'
        self.client_id = client_id
        self.headers = { 'Client-ID' : client_id }
        self.temp_dir = os.path.join(os.getcwd(), 'tmp')
        self.out_dir = os.path.join(os.getcwd(), out_dir)
        self.number_of_threads = number_of_threads

    def _create_login_query(self, login_ids):
        login_query = '?login='
        for login_id in login_ids:
            login_query += (login_id + ',')
        return login_query[:-1]

    def _create_url(self, query_target, query):
        return self.base_url + '/' + query_target + query
    
    def _get_access_token(self,  video_id):
        url = ACCESS_TOKEN_URL % video_id
        return requests.get(url, headers = self.headers).json()

    def _get_video_source_url(self, video_id, access_token, option = '720p60'):
        url = VIDEO_SOURCE_URL % (video_id, access_token['sig'], access_token['token'])
        res = requests.get(url, headers = self.headers).text

        url_regex = re.compile(r'https:\/\/vod-secure\.twitch\.tv\/.*%s.*\.m3u8' % option)
        return url_regex.findall(res)[0]
    
    def _get_chunk_urls(self, source, video_source_url):
        chunk_regex = re.compile(r'[0-9]+-?\w*\.ts') # Bug : '[0-9]+(-muted)?\.ts' is not working
        chunks = chunk_regex.findall(source)
        
        chunk_urls = [None] * len(chunks)
        base_chunk_url = re.sub(r'(\w|-)+\.m3u8', '', video_source_url)
        for i, chunk in enumerate(chunks):
            chunk_urls[i] = {
                'url': base_chunk_url + chunk,
                'index': i
            }
        return chunk_urls

    def _get_chunk(self, chunk_url):
        res = requests.get(chunk_url['url'])
        return res.content

    def _merge_chunks(self, user_id, video_id, number_of_chunks):
        result = open(os.path.join(self.temp_dir, '%s_%s.mp4' % (user_id, video_id)), 'w+')
        for i in range(0, number_of_chunks):
            with open(os.path.join(self.temp_dir, '%d.ts' % i), 'r') as f:
                result.write(f)
                f.close()
        print('A')

    def _download_video(self, user_id, video_id, video_source_url):
        res = requests.get(video_source_url).text
        chunk_urls = self._get_chunk_urls(res, video_source_url)

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.mkdir(self.temp_dir)

        thread_pool = ThreadPool(NUMBER_OF_THREADS)
        results = thread_pool.map(self._get_chunk, chunk_urls)
        
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
    
        with open(os.path.join(self.out_dir, '%s_%s.mp4' % (user_id, video_id)), 'wb') as f:
            f.write(b'\n'.join(results))
        
        shutil.rmtree(self.temp_dir)

    def Users(self, login_ids,  filter = []):
        login_query = self._create_login_query(login_ids)
        url = self._create_url('users', login_query)
        res = requests.get(url, headers = self.headers).json()
        return  dict((data['login'], {'id' : data['id'], 'display_name' : data['display_name']}) for data in res['data'])

    def Videos(self, users,  filter = []):
        videos = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/videos?sort=time' +  '&user_id=' + data['id'], headers = self.headers).json()
            video = list(map(lambda  x : {
                'title': x['title'],
                'id' : x['id'],
                'duration' : x['duration'],
                'created_at' : x['created_at'],
                'view_count' : x['view_count']
                }, res['data']))
            videos[user] = video
        return videos

    def Test(self):
        users = self.Users(['nanayango3o'])
        videos = self.Videos(users)
        resolution_regex = re.compile(r'(([0-9]+p[0-9]+)|chunked|audio_only)')
        access_token = self._get_access_token(videos['nanayango3o'][3]['id'])
        video_source_url = self._get_video_source_url(videos['nanayango3o'][3]['id'], access_token, option = '160p30')
        
        self._download_video('nanayango3o', videos['nanayango3o'][3]['id'], video_source_url)

test = VodDownloader(
    client_id = '',
    out_dir = 'dist',
    number_of_threads = 10,
)
test.Test()
