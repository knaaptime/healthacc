import pandas as pd
import requests


def feeds_from_bbox(bbox):
    """Generate a dict of GTFS feeds by querying the transitland api with a bounding box

    Parameters
    ----------
    bbox : list-like
        A list or tuple of bounding box coordinates formatted as (lng_max, lat_min, lng_min, lat_max). e.g. For a geodataframe
        stored in epsg 4326, this can be obtained with geodataframe.total_bounds

    Returns
    -------
    dict
        dictorionary of gtfs feeds formatted as {`provider_name`: `url`}. 
        This dict can be fed directly to ua.gtfsfeeds.feeds.add_feed(
    """
    bbox = ",".join([str(i) for i in bbox])
    q = requests.get(f"https://transit.land/api/v1/feeds?bbox={bbox}&per_page=1000")
    feeds = pd.DataFrame.from_records(q.json()["feeds"])
    # several providers are missing names, but the `onestop_id` field appears to have useful info
    feeds.onestop_id = (
        feeds.onestop_id.str.split("-")
        .apply(lambda x: x[-1])
        .str.split("~")
        .apply(lambda x: x[0])
    )
    feeds.name = feeds.name.fillna(feeds.onestop_id)
    feeds = (
        feeds[["name", "url"]].dropna(subset=["url"]).set_index("name").to_dict()["url"]
    )
    return feeds
