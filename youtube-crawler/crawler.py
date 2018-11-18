import requests

class Crawler:
  def __init__(self,
               base_url = 'https://www.googleapis.com/youtube/v3/channels',
               api_key = '',
               parts = 'id, snippet, brandingSettings, contentDetails, invideoPromotion, statistics, topicDetails',
               ids = [],
               headers = {}):
    self.base_url = base_url
    self.api_key = 'key=' + api_key
    self.parts = 'part=' + parts
    self.ids = ids
    self.headers = headers
  
  def _query(self, id):
    return '?id=' + id + '&' + self.api_key + '&' + self.parts
  
  def Run(self):
    for id in self.ids.values():
      res = requests.get(self.base_url + self._query(id), headers = self.headers)
      print(res.json())

if __name__ == '__main__':
 
  base_url = 'https://www.googleapis.com/youtube/v3/channels'
  api_key = ''
  parts =  'id, snippet, statistics'
  ids = {
    '흐쟁이' : 'UCWOx-QEaE9bjGHhO5J1mgpQ'
  }
  headers = {}

  youtube_crawler = Crawler(base_url = base_url,
                            api_key = api_key,
                            parts = parts,
                            ids = ids,
                            headers = headers)
  youtube_crawler.Run()
