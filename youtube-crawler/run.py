from crawler.Crawler import Crawler
import os
import json
import sys
import time

def Run(index_file = 'youtube-index.json',
        out_dir = 'dist'):
    base_dir = os.path.dirname(__file__)
    try:
        with open(os.path.join(base_dir, index_file), encoding='utf-8') as f:
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
    with open(os.path.join(base_dir, targets), encoding='utf-8') as f:
        targets = json.load(f)
    
    output = {}

    output['Channels'] = crawler.Channels(targets)
    print('channels done')
    video_lists = crawler.SearchVideos(targets)
    output['Videos'] = crawler.Videos(targets, video_lists)
    print('videos done')

    #############################################################
    
    out_dir = os.path.join(base_dir, out_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    with open(out_dir + '/' + t + '.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
        print('end crawling')

if __name__ == '__main__':
    Run()
