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
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'], headers = self.headers).json()
            channel = self._filter(res, filter)
            channels[user['display_name']] = channel
        return channels

    def Follows(self, users):
        follows = {}
        for user in users:
            follow = []
            offset = 0
            while True:
                res = requests.get(self.base_url + '/users/' + user['_id'] + '/follows/channels?limit=100' + '&offset=' + str(offset), headers = self.headers).json()
                if len(res['follows']) == 0: break
                follow += list(map(lambda  x : x['channel']['display_name'], res['follows']))
                offset += 100
            follows[user['display_name']] = follow
        return follows

    def Teams(self, users):
        teams = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/teams', headers = self.headers).json()
            team = list(map(lambda  x : x['display_name'], res['teams']))
            teams[user['display_name']] = team
        return teams

    # TODO : Not athorized
    def Subscribers(self, users,  filter = []):
        auth_headers = {
            'Client-ID' : self.client_id,
            'Accept' : 'application/vnd.twitchtv.v5+json',
            'Authorization' : 'OAuth ' + self._oauth('channel_subscriptions') 
        }
        subscribers = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/subscriptions', headers = auth_headers).json()
            subscriber = self._filter(res, filter)
            subscribers[user['display_name']] = subscriber
        return subscribers
    
    def Videos(self, users,  filter = []):
        videos = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/videos?limit=20&sort=time', headers = self.headers).json()
            video = list(map(lambda  x : { 'game' : x['game'], 'views' : x['views'] }, res['videos']))
            videos[user['display_name']] = video
        return videos

    def Stream_by_User(self, users, filter = []):
        streams = {}
        for user in users:
            res = requests.get(self.base_url + '/streams/' + user['_id'], headers = self.headers).json()
            if res['stream'] == None: continue
            stream = self._filter(res['stream'], filter)
            streams[user['display_name']] = stream
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

###########################################################################
# How to use?
#
# Example
#
# try:
#     with open(index_file, encoding='utf-8') as f:
#         index = json.load(f)
#         client_id = index['client-ID']
#         targets = index['targets']
#         client_secret = ''
# except:
#     print("No index file")
#     sys.exit(1)

# ############################################################
# # Get current time
# t = time.strftime('%y%m%d%H%M')
# new_day = int(t[-4:]) < 15 

# crawler = Crawler(client_id = client_id, client_secret = client_secret)
# with open(targets, encoding='utf-8') as f:
#     targets = json.load(f)

# output = {}
# output['users'] = users = crawler.Users(targets.values())

# #############################################################
# # Collect data with 15 minute period
# output['streams'] = crawler.Stream_by_User(users)
# output['live_streams'] = crawler.Live_Streams()
# output['top_game'] = crawler.Top_Game()
# output['stream_summary'] = crawler.Stream_Summary()

# #############################################################
# # Collect data with 1 day period
# if new_day :
#     output['channels'] = crawler.Channel_by_ID(users)
#     output['follows'] = crawler.Follows(users)
#     output['teams'] = crawler.Teams(users)
#     output['videos'] = crawler.Videos(users)

# if not os.path.exists(out_dir):
#     os.mkdir(out_dir)

# with open(out_dir + '/' + t + '.json', 'w', encoding='utf-8') as f:
#     json.dump(output, f, ensure_ascii=False)

# ###################################################
# # TODO
# # Requests which needs oauth
# #subscribers = crawler.Subscribers(users)
