import pandas as pd
import json
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory

# navp2geojson.py
# Read navp (internal) navigation solution and make a geojson-output.
# Joakim Skjefstad

def navp_trajectory(mission_folder_path: Path, nth_row=1):
    mission_name = mission_folder_path.name
    format_file_path = mission_folder_path / Path(r"cp\data\format.txt")
    navpos_file_path = mission_folder_path / Path(r"cp\data\navpos.txt")

    # Parse format.txt to find relevant columns for NAV_LATITUDE and NAV_LONGITUDE
    columns_mapping = {}
    with open(format_file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            #print(parts)

            #if len(parts) == 2 and 'Time' in parts[1]:
            #    columns_mapping['Time'] = int(parts[0].strip())
            #    print("Time col:", columns_mapping['Time'])
            # Hardcode time col...
            columns_mapping['Time'] = 1

            if len(parts) == 2 and 'NAVIGATION_SYSTEM_DATA    NAV_LATITUDE' in parts[1]:
                columns_mapping['NAV_LATITUDE'] = int(parts[0].strip())
                
            if len(parts) == 2 and 'NAVIGATION_SYSTEM_DATA    NAV_LONGITUDE' in parts[1]:
                columns_mapping['NAV_LONGITUDE'] = int(parts[0].strip())

    # Read navpos.txt into a DataFrame
    navpos_df = pd.read_csv(
        navpos_file_path,
        sep=r'\s+',
        header=None,
        usecols=[columns_mapping['Time'] - 1,columns_mapping['NAV_LATITUDE'] - 1, columns_mapping['NAV_LONGITUDE'] -1],  # Adjust to 0-based indexing
        names=['Time', 'NAV_LATITUDE', 'NAV_LONGITUDE']
    )

    print(navpos_df)

    mission_starttime = pd.to_datetime(navpos_df['Time'].iloc[0], unit='s')
    mission_endtime = pd.to_datetime(navpos_df['Time'].iloc[-1], unit='s')

    mission_startcoordinates = navpos_df[['NAV_LONGITUDE', 'NAV_LATITUDE']].iloc[0].values.tolist()
    mission_endcoordinates = navpos_df[['NAV_LONGITUDE', 'NAV_LATITUDE']].iloc[-1].values.tolist()

    # Create a GeoJSON LineString from NAV_LATITUDE and NAV_LONGITUDE, selecting only every nth_row rows
    coordinates = navpos_df[['NAV_LONGITUDE', 'NAV_LATITUDE']].iloc[::nth_row].values.tolist()

    geojson_startpoint = {
        "type": "Point",
        "coordinates": mission_startcoordinates
    }
    geojson_endpoint = {
        "type": "Point",
        "coordinates": mission_endcoordinates
    }
    
    startpoint_feature = {
        "type": "Feature",
        "geometry": geojson_startpoint,
        "properties": {"name": "Mission start",
                    "mission_name": mission_name,
                    "mission_starttime_utc" : mission_starttime.strftime('%Y-%m-%d %H:%M:%S')
                    }
    }

    endpoint_feature = {
        "type": "Feature",
        "geometry": geojson_endpoint,
        "properties": {"name": "Mission stop",
                    "mission_name": mission_name,
                    "mission_endtime_utc" : mission_endtime.strftime('%Y-%m-%d %H:%M:%S')
                    }
    }

    trajectory_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {
                    "mission_name": mission_name,
                    "mission_starttime_utc" : mission_starttime.strftime('%Y-%m-%d %H:%M:%S'),
                    "mission_endtime_utc" : mission_endtime.strftime('%Y-%m-%d %H:%M:%S')
                }
            }

    feature_collection = {
        "type": "FeatureCollection",
        "features": [startpoint_feature, trajectory_feature, endpoint_feature]
    }

    return feature_collection

def select_mission_folder():
    Tk().withdraw()

    mission_folder = askdirectory(title="Select missionfolder")
    if not mission_folder:
        print("No folder selected. Exiting.")
        return []
    return Path(mission_folder)

if __name__ == "__main__":    
    mission_folder_path = select_mission_folder()

    mission_name = mission_folder_path.name
    print(mission_name)
    print(mission_folder_path)


    navp_trajectory_geojson = navp_trajectory(mission_folder_path, nth_row=5)

    output_filename = f"{mission_name}_internal_navigation.geojson"
    with open(output_filename, 'w') as geojson_file:
        json.dump(navp_trajectory_geojson, geojson_file, indent=2)