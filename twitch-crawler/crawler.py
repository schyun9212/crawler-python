import requests
import os
import json

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
    
    def Users(self, names):
        query = self._login(names)
        res = requests.get(self.base_url + '/users' + query, headers = self.headers)
        return res.json()['users']

    def Channel_by_ID(self, users):
        channels = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'], headers = self.headers)
            channel = res.json()
            channels[user['display_name']] = channel
        return channels

    def Follows(self, users):
        follows = {}
        for user in users:
            res = requests.get(self.base_url + '/users/' + user['_id'] + '/follows/channels?limit=100', headers = {'Client-ID' : self.client_id })
            follow =  res.json()
            follows[user['display_name']] = follow
        return follows

    def Teams(self, users):
        teams = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/teams', headers = self.headers)
            team = res.json()
            teams[user['display_name']] = team
        return teams

    def Subscribers(self, users):
        auth_headers = {
            'Client-ID' : client_id,
            'Accept' : 'application/vnd.twitchtv.v5+json',
            'Authorization' : 'OAuth ' + self._oauth('channel_subscriptions') 
        }
        subscribers = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/subscriptions', headers = auth_headers)
            subscriber = res.json()
            subscribers[user['display_name']] = subscriber
        return subscribers
    
    def Videos(self, users):
        videos = {}
        for user in users:
            res = requests.get(self.base_url + '/channels/' + user['_id'] + '/videos', headers = self.headers)
            video = res.json()['videos']
            videos[user['display_name']] = video
        return videos

    def Stream_by_User(self, users):
        streams = {}
        for user in users:
            res = requests.get(self.base_url + '/streams/' + user['_id'], headers = self.headers)
            stream = res.json()['videos']
            streams[user['display_name']] = stream
        return streams
    
    def Top_Game(self):
        res = requests.get(self.base_url + '/games/top', headers = self.headers)
        return res.json()

if __name__ == '__main__':
    client_id = ''
    client_secret = ''

    crawler = Crawler(client_id = client_id, client_secret = client_secret)
    with open('data/targets.json', encoding='utf-8') as f:
        targets = json.load(f)
    users = crawler.Users(targets.values())
    channels = crawler.Channel_by_ID(users)
    follows = crawler.Follows(users)
    teams = crawler.Teams(users)
    videos = crawler.Videos(users)
    top_game = crawler.Top_Game()

    ###################################################
    # TODO
    # Requests which needs oauth
    #subscribers = crawler.Subscribers(users)


    print('a')
