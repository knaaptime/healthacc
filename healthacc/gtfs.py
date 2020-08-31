import pandas as pd
import requests

def feeds_from_bbox(bbox):
    bbox = ",".join([str(i) for i in bbox])
    q = requests.get(f"https://transit.land/api/v1/feeds?bbox={bbox}&per_page=1000")
    feeds = pd.DataFrame.from_records(q.json()['feeds'])
    # several providers are missing names, but the `onestop_id` field appears to have useful info
    feeds.onestop_id = feeds.onestop_id.str.split('-').apply(lambda x: x[-1]).str.split('~').apply(lambda x: x[0])
    feeds.name = feeds.name.fillna(feeds.onestop_id)
    feeds = feeds[['name', 'url']].dropna(subset=['url']).set_index('name').to_dict()['url']
    return feeds