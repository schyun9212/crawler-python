from crawler.Crawler import Crawler
import os
import json
import sys
import time

def Run(index_file = 'twitch-index.json',
        out_dir = 'dist'):
    base_dir = os.path.dirname(__file__)
    try:
        with open(os.path.join(base_dir, index_file), encoding='utf-8') as f:
            index = json.load(f)
            client_id = index['client-ID']
            client_secret = ''
    except:
        print("No index file")
        sys.exit(1)

    ############################################################
    # Get current time
    t = time.strftime('%y%m%d%H%M')
    t = '0000000000'
    new_day = int(t[-4:]) < 30 

    crawler = Crawler(client_id = client_id, client_secret = client_secret)
    with open(os.path.join(base_dir, index['targets']), encoding='utf-8') as f:
        targets = json.load(f)
    with open(os.path.join(base_dir, index['filters']), encoding='utf-8') as f:
        filters = json.load(f)
    
    users = crawler.Users(targets.values())

    #############################################################
    # Collect data with 30 minute period
    streams= crawler.Stream_by_User(users, filters['stream_by_user'])
    print('streams done')
    live_streams = crawler.Live_Streams()
    print('live_streams done')
    top_game = crawler.Top_Game()
    print('top_game done')
    stream_summary = crawler.Stream_Summary()
    print('stream_summary done')

    #############################################################
    # Collect data with 1 day period

    if new_day :
        channels = crawler.Channel_by_ID(users, filters['channel_by_id'])
        print('channels done')
        follows = crawler.Follows(users)
        print('follows done')
        teams = crawler.Teams(users)
        print('teams done')
        #videos = crawler.Videos(users)
        #print('videos done')
    
    out_dir = os.path.join(base_dir, out_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    for user, data in users.items():
        if user in streams:
            data['streams'] = streams[user]
        
        if new_day:
            data['channels'] = channels[user]
            data['follows'] = follows[user]
            data['teams'] = teams[user]
            #data['videos'] = videos[user]
            
    with open(out_dir + '/' + t + '.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False)
        print('end crawling')

if __name__ == '__main__':
    Run('twitch-index.json', 'dist')
