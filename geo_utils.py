import os 
import pandas as pd

import pickle
from typing import Any

from geopy.geocoders import Nominatim
import networkx as nx
import osmnx as ox
from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode

gis = GIS()

def get_lat_long(city):
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="city_locator")

    try:
        # Get location information for the given city
        location = geolocator.geocode(city)

        if location:
            # Extract latitude and longitude
            lat, lon = location.latitude, location.longitude
            return lat, lon
        else:
            return None  # If location information is not found

    except Exception as e:
        print(f"Error: {e}")
        return None
    
class DistanceMesure:
    def __init__(self, city_name):
        self.city_name = city_name
        self.set_graph(city_name)
        
    def set_graph(self, city_name):
        if os.path.exists(f"{city_name}.p"):
            self.G = pickle.load(open(f"{city_name}.p", "rb"))
        else:
            lat, long = get_lat_long(city_name)
            self.G = ox.graph_from_point((lat, long), dist=1000, network_type="drive")
            self.G = ox.speed.add_edge_speeds(self.G)
            self.G = ox.speed.add_edge_travel_times(self.G)
            pickle.dump(self.G, open(f"{city_name}.p", "wb"))

    

    def get_routes_dist(self, point1, point2, plot=False):
        orig_node = ox.nearest_nodes(self.G, X=point1[1], Y=point1[0])
        dest_node = ox.nearest_nodes(self.G, X=point2[1], Y=point2[0])
        route = self.shortest_path(orig_node, dest_node)
        gdf = ox.utils_graph.route_to_gdf(self.G, route)
        if plot:
            fig, ax = ox.plot_graph_route(self.G, route ,route_color="y", route_linewidth=4, node_size=0)
        return {"length" : gdf["length"].sum()/1000, "travel_time" : gdf["travel_time"].sum()/60}

    def shortest_path(self, orig_node, dest_node):
        return nx.shortest_path(self.G, orig_node, dest_node)

def load_list_poi(csv_file = "list_poi.csv"):
    return list(pd.read_csv(csv_file, header=None)[0])

def get_poi(lat, long, list_poi = None, geocode_args = {'max_locations':200}):

    location ={
        'Y' : lat,
        'X' : long,
    }

    if list_poi is None:
        list_poi = load_list_poi()

    df = pd.DataFrame()
    for poi in list_poi:
        address = {
            'category': poi,
            'location': location
        }
        df = pd.concat([df, pd.DataFrame(geocode(address, **geocode_args))])

    return df

def dict_to_col(df, dict_col, key):
    return df[dict_col].apply(lambda loc: loc[key])

def auto_clean_poi(df):
    df['latitude'] = df['location'].apply(lambda loc: loc['y'])
    df['longitude'] = df['location'].apply(lambda loc: loc['x'])
    df['type'] = df['attributes'].apply(lambda loc: loc['Type'])
    df['phone'] = df['attributes'].apply(lambda loc: loc['Phone'])
    df['url'] = df['attributes'].apply(lambda loc: loc['URL'])

    df.drop(['location'], axis=1, inplace=True)
    df.drop(['attributes'], axis=1, inplace=True)
    df.drop(['extent'], axis=1, inplace=True)
    return df

