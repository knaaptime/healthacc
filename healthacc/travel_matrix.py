
import pandas as pd
from tqdm.auto import tqdm

def compute_travel_cost_adjlist(origins, destinations, network, reindex_orig=None, reindex_dest=None):
    origins = origins.copy()
    destinations = destinations.copy()
    
    origins['osm_ids'] = network.get_node_ids(origins.centroid.x, origins.centroid.y).astype(int)
    destinations['osm_ids'] = network.get_node_ids(destinations.centroid.x, destinations.centroid.y).astype(int)
    
    ods = []
    
    # I dont think there's a way to do this in parallel, so we can at least show a progress bar
    with tqdm(total=len(origins['osm_ids'])) as pbar:
        for origin in origins['osm_ids']:
            df = pd.DataFrame()
            df['cost'] = network.shortest_path_lengths([int(origin)] * len(origins), destinations['osm_ids'])
            if reindex_dest:
                df['destination'] = destinations[reindex_dest].values
                df['origin'] = origins[origins.osm_ids==origin][reindex_orig].values[0]
            else:
                df['destination'] = destinations['osm_ids']
                df['origin'] = origin
            ods.append(df)
            pbar.update(1)
    
    combined = pd.concat(ods)
    
    return combined
    

def compute_travel_cost_matrix(origins, destinations, network, reindex_name=False):
    origins = origins.copy()
    destinations = destinations.copy()
    
    origins['osm_ids'] = network.get_node_ids(origins.centroid.x, origins.centroid.y).astype(int)
    destinations['osm_ids'] = network.get_node_ids(destinations.centroid.x, destinations.centroid.y).astype(int)
    
    ods = {}

    with tqdm(total=len(origins['osm_ids'])) as pbar:
        for origin in origins['osm_ids']:
            ods[f"{origin}"] = network.shortest_path_lengths([int(origin)] * len(origins), destinations['osm_ids'])
            pbar.update(1)
    
    if reindex_name:
        df = pd.DataFrame(ods, index=origins[reindex_name])
        df.columns = df.index
    else:
        df = pd.DataFrame(ods, index=origins)
    
    return df