import pandas as pd
from tqdm.auto import tqdm


def compute_travel_cost_adjlist(
    origins, destinations, network, index_orig=None, index_dest=None
):
    """Generate travel cost adjacency list.

    Parameters
    ----------
    origins : geopandas.GeoDataFrame
        a geodataframe containing the locations of origin features
    destinations : geopandas.GeoDataFrame
        a geodataframe containing the locations of destination features
    network : pandana.Network
        pandana Network instance for calculating the shortest path between origins and destinations
    index_orig : str, optional
        Unique index on the origins dataframe.
    index_dest : str, optional
        Unique index on the destinations dataframe.
    Returns
    -------
    pandas.DataFrame
        pandas DataFrame containing the shortest-cost distance from each origin feature to each destination feature
    """
    origins = origins.copy()
    destinations = destinations.copy()

    origins["osm_ids"] = network.get_node_ids(
        origins.centroid.x, origins.centroid.y
    ).astype(int)
    destinations["osm_ids"] = network.get_node_ids(
        destinations.centroid.x, destinations.centroid.y
    ).astype(int)

    ods = []

    if not index_orig:
        origins['idx'] = origins.index.values
        index_orig = 'idx'
    if not index_dest:
        destinations['idx'] = destinations.index.values
        index_dest = 'idx'

    # I dont think there's a way to do this in parallel, so we can at least show a progress bar
    with tqdm(total=len(origins["osm_ids"])) as pbar:
        for origin in origins["osm_ids"]:
            df = pd.DataFrame()
            df["cost"] = network.shortest_path_lengths(
                [origin for d in destinations["osm_ids"]],
                [d for d in destinations["osm_ids"]],
            )
            df["destination"] = destinations[index_dest].values
            df["origin"] = origins[origins.osm_ids == origin][index_orig].values[
                0
            ]

            ods.append(df)
            pbar.update(1)

    combined = pd.concat(ods)

    return combined

