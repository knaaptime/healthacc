import osmnet
import pandas as pd
import pandana as pdna
import urbanaccess as ua
from . import feeds_from_bbox


def multimodal_from_bbox(
    bbox,
    gtfs_dir=None,
    save_osm=None,
    save_gtfs=None,
    excluded_feeds=None,
    transit_net_kwargs=None,
    headways=False,
    additional_feeds=None
):
    """Generate a combined walk/transit pandana Network from a bounding box of latitudes and longitudes

    Parameters
    ----------
    bbox : tuple
        A bounding box formatted as (lng_max, lat_min, lng_min, lat_max). e.g. For a geodataframe
        stored in epsg 4326, this can be obtained with geodataframe.total_bounds
    gtfs_dir : str, optional
        path to directory for storing downloaded GTFS data. If None, the current directory will be used
    save_osm : str, optional
        Path to store the intermediate OSM Network as an h5 file
    save_gtfs : str, optional
        Path to store the intermediate GTFS Network as an h5 file
    excluded_feeds : list, optional
        list of feed names to exclude from the GTFS downloaded
    transit_net_kwargs : dict, optional
        additional keyword arguments to be passed to the urbanaccess GTFS network instantiator.
        defaults to {'day':"monday", 'timerange':["07:00:00", "10:00:00"]}
    headways : bool, optional
        Whether to include headway calculations for the combined network
    additional_feeds : dict, optional
        Dictionary of additional feed locations in case they are not hosted on transitland.
        Should be specified as {transitagencyname: url} 

    Returns
    -------
    pandana.Network
        a multimodal (walk/transit) Network object built from OSM and GTFS data that lie within the bounding box
    """    
    assert bbox is not None, "You must provide a bounding box to collect network data"
    if not gtfs_dir:
        gtfs_dir="."

    if not transit_net_kwargs:
        transit_net_kwargs = dict(
            day="monday", timerange=["07:00:00", "10:00:00"], calendar_dates_lookup=None
        )


    # Get gtfs data
    feeds = feeds_from_bbox(bbox)

    if excluded_feeds:  # remove problematic feeds if necessary
        for feed in list(feeds.keys()):
            if feed in excluded_feeds:
                feeds.pop(feed)
    
    if len(ua.gtfsfeeds.feeds.to_dict()["gtfs_feeds"]) > 0:
        ua.gtfsfeeds.feeds.remove_feed(
            remove_all=True
        )  # feeds object is global so reset it if there's anything leftover
    
    ua.gtfsfeeds.feeds.add_feed(feeds)
    if additional_feeds:
        ua.gtfsfeeds.feeds.add_feed(additional_feeds)

    ua.gtfsfeeds.download()

    loaded_feeds = ua.gtfs.load.gtfsfeed_to_df(
        f"{gtfs_dir}/data/gtfsfeed_text/", bbox=bbox, remove_stops_outsidebbox=True
    )
    if save_gtfs:
        ua_to_h5(loaded_feeds, f"{gtfs_dir}/{save_gtfs}")


    # Get OSM data
    nodes, edges = osmnet.network_from_bbox(bbox=bbox)
    osm_network = pdna.Network(
        nodes["x"], nodes["y"], edges["from"], edges["to"], edges[["distance"]]
    )
    if save_osm:
        osm_network.save_hdf5(save_osm)


    # Create the transit network
    ua.create_transit_net(gtfsfeeds_dfs=loaded_feeds, **transit_net_kwargs)
    osm_network.nodes_df['id'] = osm_network.nodes_df.index

    ua.create_osm_net(
        osm_edges=osm_network.edges_df,
        osm_nodes=osm_network.nodes_df,
        travel_speed_mph=3,
    )
    if headways:
        ua.gtfs.headways.headways(
            gtfsfeeds_df=loaded_feeds, headway_timerange=transit_net_kwargs["timerange"]
        )
        ua.network.integrate_network(
            urbanaccess_network=ua.ua_network,
            headways=True,
            urbanaccess_gtfsfeeds_df=loaded_feeds,
            headway_statistic="mean",
        )
    else:
        ua.integrate_network(urbanaccess_network=ua.ua_network, headways=False)

    combined_net = pdna.Network(
        ua.ua_network.net_nodes["x"],
        ua.ua_network.net_nodes["y"],
        ua.ua_network.net_edges["from_int"],
        ua.ua_network.net_edges["to_int"],
        ua.ua_network.net_edges[["weight"]],
    )

    return combined_net


def ua_to_h5(loaded_feeds, path):

    hdf = pd.HDFStore(path)
    hdf["calendar"] = loaded_feeds.calendar
    hdf["calendar_dates"] = loaded_feeds.calendar_dates
    hdf["headways"] = loaded_feeds.headways
    hdf["routes"] = loaded_feeds.routes
    hdf["stop_times"] = loaded_feeds.stop_times
    hdf["stop_times_int"] = loaded_feeds.stops
    hdf["stops"] = loaded_feeds.stops
    hdf["trips"] = loaded_feeds.trips
    hdf.close()
