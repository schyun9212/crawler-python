import requests

class Crawler:
    def __init__(self, client_id, client_secret):
        self.base_url = 'https://api.twitch.tv/kraken'
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            'Client-ID' : client_id,
            'Accept' : 'application/vnd.twitchtv.v5+json'
        }
    
    def _oauth(self, scope):
        res = requests.post('https://id.twitch.tv/oauth2/token?'
                    + 'client_id=' + self.client_id
                    + '&client_secret=' + self.client_secret
                    + '&grant_type=client_credentials'
                    + '&scope=' + scope)
        return res.json()['access_token']

    def _login(self, names):
        login = '?login='
        for name in names:
            login += (name + ',')
        return login[:-1]


    def _filter(self, data, keys):
        filtered_data = data
        for key in keys:
            del filtered_data[key]
        return filtered_data
    
    def Users(self, names,  filter = []):
        query = self._login(names)
        res = requests.get(self.base_url + '/users' + query, headers = self.headers).json()
        return  dict((k['display_name'], {'_id' : k['_id'], 'logo' : k['logo']}) for k in res['users'])

    def Channel_by_ID(self, users,  filter = []):
        channels = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/channels/' + data['_id'], headers = self.headers).json()
            channel = self._filter(res, filter)
            channels[user] = channel
        return channels

    def Follows(self, users):
        follows = {}
        for user, data in users.items():
            follow = []
            offset = 0
            while True:
                res = requests.get(self.base_url + '/users/' + data['_id'] + '/follows/channels?limit=100' + '&offset=' + str(offset), headers = self.headers).json()
                if len(res['follows']) == 0: break
                follow += list(map(lambda  x : x['channel']['display_name'], res['follows']))
                offset += 100
            follows[user] = follow
        return follows

    def Teams(self, users):
        teams = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/channels/' + data['_id'] + '/teams', headers = self.headers).json()
            team = list(map(lambda  x : x['display_name'], res['teams']))
            teams[user] = team
        return teams

    # TODO : Not athorized
    def Subscribers(self, users,  filter = []):
        auth_headers = {
            'Client-ID' : self.client_id,
            'Accept' : 'application/vnd.twitchtv.v5+json',
            'Authorization' : 'OAuth ' + self._oauth('channel_subscriptions') 
        }
        subscribers = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/channels/' + data['_id'] + '/subscriptions', headers = auth_headers).json()
            subscriber = self._filter(res, filter)
            subscribers[user] = subscriber
        return subscribers
    
    def Videos(self, users,  filter = []):
        videos = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/channels/' + data['_id'] + '/videos?limit=20&sort=time', headers = self.headers).json()
            video = list(map(lambda  x : { 'game' : x['game'], 'views' : x['views'] }, res['videos']))
            videos[user] = video
        return videos

    def Stream_by_User(self, users, filter = []):
        streams = {}
        for user, data in users.items():
            res = requests.get(self.base_url + '/streams/' + data['_id'], headers = self.headers).json()
            if res['stream'] == None:
                streams[user] = {} 
                continue
            stream = self._filter(res['stream'], filter)
            streams[user] = stream
        return streams
    
    def Live_Streams(self,  filter = []):
        res = requests.get(self.base_url + '/streams/' + '?language=ko&limit=100', headers = self.headers).json()
        return self._filter(res, filter)
    
    def Top_Game(self,  filter = []):
        res = requests.get(self.base_url + '/games/top', headers = self.headers).json()
        return self._filter(res, filter)
    
    def Stream_Summary(self,  filter = []):
        res = requests.get(self.base_url + '/streams/summary', headers = self.headers).json()
        return self._filter(res, filter)