from crawler.Crawler import Crawler
import os
import json
import sys
import time

def Run(index_file = 'twitch-index.json',
        out_dir = 'dist'):
    try:
        with open(index_file, encoding='utf-8') as f:
            index = json.load(f)
            client_id = index['client-ID']
            targets = index['targets']
            client_secret = ''
    except:
        print("No index file")
        sys.exit(1)

    ############################################################
    # Get current time
    t = time.strftime('%y%m%d%H%M')
    new_day = int(t[-4:]) < 15 

    crawler = Crawler(client_id = client_id, client_secret = client_secret)
    with open(targets, encoding='utf-8') as f:
        targets = json.load(f)
    
    output = {}
    output['users'] = users = crawler.Users(targets.values())

    #############################################################
    # Collect data with 15 minute period
    output['streams'] = crawler.Stream_by_User(users)
    output['live_streams'] = crawler.Live_Streams()
    output['top_game'] = crawler.Top_Game()
    output['stream_summary'] = crawler.Stream_Summary()

    #############################################################
    # Collect data with 1 day period
    if new_day :
        output['channels'] = crawler.Channel_by_ID(users)
        output['follows'] = crawler.Follows(users)
        output['teams'] = crawler.Teams(users)
        output['videos'] = crawler.Videos(users)
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    with open(out_dir + '/' + t + '.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)

if __name__ == '__main__':
    Run()
