import requests
import datetime as dt

class Crawler:
  def __init__(self,
               api_key = ''):
    self.base_url = 'https://www.googleapis.com/youtube/v3'
    self.api_key = api_key
  
  def _query(self, identifier, part):
    return '?id=' + identifier + '&' + 'key=' + self.api_key + '&' + 'part=' + part
  
  def Channels(self, users):
    part = 'statistics'

    channels = {}
    for name, identifier in users.items():
      res = requests.get(self.base_url + '/channels' + self._query(identifier, part))
      channel = res.json()
      channels[name] = channel['items'][0]['statistics']
    
    return channels

  def SearchVideos(self, users):
    part = 'snippet'
    video_lists = {}

    month_ago = dt.date.today() - dt.timedelta(days = 28)
    after = '2018-{:2d}-{:2d}T00:00:00Z'.format(month_ago.month, month_ago.day)
    for name, identifier in users.items():
      res = requests.get(self.base_url + '/search' + self._query(identifier, part)
                        + '&channelId=' + identifier
                        + '&type=video'
                        + '&order=date'
                        + '&maxResults=50'
                        + '&publishedAfter=' + after)
      video_list = [x['id']['videoId'] for x in res.json()['items']]

      while ('nextPageToken' in res.json()):
          res = requests.get(self.base_url + '/search' + self._query(identifier, part)
                    + '&channelId=' + identifier
                    + '&type=video'
                    + '&order=date'
                    + '&maxResults=50'
                    + '&publishedAfter=' + after
                    + '&pageToken=' + res.json()['nextPageToken'])
          video_list += [x['id']['videoId'] for x in res.json()['items']]

      video_lists[name] = video_list
    return video_lists

  def _video_query(self, video_list, part):
    query = '?key=' + self.api_key + '&part=' + part + '&id='
    for video in video_list:
      query +=  video + ','
    return query[:-1]

  def Videos(self, users, video_lists):
    part = 'snippet,liveStreamingDetails,statistics,topicDetails'
    videos = {}
    for name, identifier in users.items():
      res = requests.get(self.base_url + '/videos' + self._video_query(video_lists[name], part))
      video = res.json()['items']
      videos[name] = [{'tags' : x['snippet']['tags'], 'statistics' : x['statistics'], 'topicDetails' : x['topicDetails']} for x in video]

    return videos