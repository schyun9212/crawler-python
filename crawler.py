import requests

class Crawler:
    def __init__(self, client_id, streamers):
        self.base_url = 'https://api.twitch.tv/helix'
        self.client_id = client_id
        self.streamers = streamers
        self.headers = {
            'Client-ID' : client_id
        }
        
        self.login = self._login(streamers)
        self.streamer_ids = {}

    def _login(self, streamers):
        login = '?'
        for s in streamers:
            login += ('login=' + s + '&')
        return login

    def _streamer_ids(self, response):
        ids = {}
        for datum in response.json()['data']:
            ids[datum['login']] = datum['id']
        return ids

    def _users(self):
        res = requests.get(self.base_url + '/users' + self.login, headers = self.headers)
        self.users = res.json()

        for datum in self.users['data']:
            self.streamer_ids[datum['login']] = datum['id']
    
    def _follows(self):
        for sid in self.streamer_ids.values():
            res = requests.get(self.base_url + '/users/follows?from_id=' + sid, headers = self.headers)
            print(res.json())

    def Run(self):
        self._users()
        self._follows()
        print(self.users)
        print(self.streamer_ids)

if __name__ == '__main__':
    client_id = ''
    streamers = ['rhdgurwns', 'rooftopcat99']

    crawler = Crawler(client_id = client_id, streamers = streamers)
    crawler.Run()
