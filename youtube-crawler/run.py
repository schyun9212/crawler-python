from crawler.Crawler import Crawler
import os
import json
import sys
import time

def Run(index_file = 'youtube-index.json',
        out_dir = 'dist'):
    try:
        with open(index_file, encoding='utf-8') as f:
            index = json.load(f)
            api_key = index['api-key']
            targets = index['targets']
    except:
        print("No index file")
        sys.exit(1)

    ############################################################
    # Get current time
    t = time.strftime('%y%m%d%H%M')

    crawler = Crawler(api_key = api_key)
    with open(targets, encoding='utf-8') as f:
        targets = json.load(f)
    
    output = {}

    output['Channels'] = crawler.Channels(targets)
    video_lists = crawler.SearchVideos(targets)
    output['Videos'] = crawler.Videos(targets, video_lists)

    #############################################################
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    with open(out_dir + '/' + t + '.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)

if __name__ == '__main__':
    Run()
