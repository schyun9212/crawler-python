import requests
import re
import os
import shutil
import subprocess
from multiprocessing.pool import ThreadPool

ACCESS_TOKEN_URL = "https://api.twitch.tv/api/vods/%s/access_token"
VIDEO_SOURCE_URL = "https://usher.ttvnw.net/vod/%s.m3u8?nauthsig=%s&nauth=%s&allow_source=true&player=twitchweb&allow_spectre=true&allow_audio_only=true"

video_options = {
    '160p30' : True,
    '360p30' : True,
    '480p30' : True,
    '720p30' : True,
    '720p60' : True,
    'audio_only' : True,
    'chunked' : True
}

class VodDownloader:
    def __init__(self, client_id, out_dir = 'dist', number_of_threads = 10):
        self.base_url = 'https://api.twitch.tv/helix'
        self.client_id = client_id
        self.headers = { 'Client-ID' : client_id }
        self.temp_dir = os.path.join(os.getcwd(), 'tmp')
        self.out_dir = os.path.join(os.getcwd(), out_dir)
        self.number_of_threads = number_of_threads

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
        with open(os.path.join(self.temp_dir, '%d.ts' % chunk_url['index']), 'wb') as chunk:
            chunk.write(res.content)
            chunk.close()

    def _merge_chunks(self, video_info, number_of_chunks):
        with open(os.path.join(self.out_dir,\
            '%s_%s_%s.mp4' % (video_info['user_name'],\
            video_info['created_at'],\
            video_info['id'])), 'wb') as video:

            for i in range(0, number_of_chunks):
                with open(os.path.join(self.temp_dir, '%d.ts' % i), 'rb') as chunk:
                    video.write(chunk.read())
                    chunk.close()
            video.close()

    def _download_video(self, video_id, video_source_url):
        video_info = self._get_video_info(video_id)

        res = requests.get(video_source_url).text
        chunk_urls = self._get_chunk_urls(res, video_source_url)

        os.mkdir(self.temp_dir)

        thread_pool = ThreadPool(self.number_of_threads)
        thread_pool.map(self._get_chunk, chunk_urls)
        
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

        return self._merge_chunks(video_info, len(chunk_urls))

    def _get_video_info(self, video_id):
        return requests.get(self._create_url('videos', '?id=%s' % video_id), headers = self.headers).json()['data'][0]

    def Download(self, video_id, option = '160p30'):
        access_token = self._get_access_token(video_id)
        video_source_url = self._get_video_source_url(video_id, access_token, option = option)
        file_name = self._download_video(video_id, video_source_url)
        print('Saved Vod(%s) as %s', (video_id, file_name))

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    '''
    def _create_login_query(self, login_ids):
        login_query = '?login='
        for login_id in login_ids:
            login_query += (login_id + ',')
        return login_query[:-1]
    
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
    '''