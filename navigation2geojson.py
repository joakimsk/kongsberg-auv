import pandas as pd
import json
import os
from pathlib import Path
import pathlib
from tkinter import Tk
from tkinter.filedialog import askdirectory
import re
import hashlib

import pynavlab


def compute_checksum(file_path):
    """Compute the SHA-256 checksum of a file."""
    hash_func = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def are_files_identical(file1, file2):
    """Check if two files are identical based on their checksum."""
    checksum1 = compute_checksum(file1)
    checksum2 = compute_checksum(file2)
    return checksum1 == checksum2

def find_navlab_versions(mission_folder_path: Path):
    default_navlab_path = mission_folder_path / Path(r"post\\navlab_smooth.bin")
    if default_navlab_path.exists():
        print("Found default navlab_smooth.bin")
    else:
        print("Did not find default navlab_smooth.bin, exiting")
        exit(-1)

    postea_search_path = mission_folder_path / Path(r"postea")

    pattern = re.compile(r"\d\d")

    alternative_navlab_solutions = [
        dir_path / Path(r"Smoothing\\PosteaSmooth-0000.bin")
        for dir_path in postea_search_path.iterdir()
        if dir_path.is_dir() and pattern.fullmatch(dir_path.name)
    ]

    #print("Alternative solutions: ", alternative_navlab_solutions)

    for idx, alt_solution_path in enumerate(alternative_navlab_solutions):
        #print("Alternative solution found:", alt_solution_path)
        if default_navlab_path.exists() and alt_solution_path.exists():
            version = alt_solution_path.parent.parent.name if alt_solution_path.parent and alt_solution_path.parent.parent else None
            if are_files_identical(default_navlab_path, alt_solution_path):
                print("Default navlab identical to", version)
            else:
                print("Default navlab different from", version)
        else:
            print("One or both files do not exist.")

    return default_navlab_path, alternative_navlab_solutions
    


def navlab_trajectory(navlab_file_path):
    n=10 # Select only every 10th row, should result in 10 Hz (100 per second in this file)
    df = pynavlab.read_navlab_smooth_to_dataframe(navlab_file_path, nth_row=n, filter_columns=["timestamp", "lat", "lon",  "depth"])
    return df

def navp_trajectory(mission_folder_path: Path):
    format_file_path = mission_folder_path / Path(r"cp\data\format.txt")
    navpos_file_path = mission_folder_path / Path(r"cp\data\navpos.txt")

    # Parse format.txt to find relevant columns for NAV_LATITUDE and NAV_LONGITUDE
    columns_mapping = {}
    with open(format_file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            #print(parts)
            if len(parts) == 2 and 'NAVIGATION_SYSTEM_DATA    NAV_LATITUDE' in parts[1]:
                columns_mapping['NAV_LATITUDE'] = int(parts[0].strip())
                
            if len(parts) == 2 and 'NAVIGATION_SYSTEM_DATA    NAV_LONGITUDE' in parts[1]:
                columns_mapping['NAV_LONGITUDE'] = int(parts[0].strip())

    # Read navpos.txt into a DataFrame
    navpos_df = pd.read_csv(
        navpos_file_path,
        sep=r'\s+',
        header=None,
        usecols=[columns_mapping['NAV_LATITUDE'] - 1, columns_mapping['NAV_LONGITUDE'] -1],  # Adjust to 0-based indexing
        names=['NAV_LATITUDE', 'NAV_LONGITUDE']
    )

    # Create a GeoJSON LineString from NAV_LATITUDE and NAV_LONGITUDE, selecting only every n rows
    n=1
    coordinates = navpos_df[['NAV_LONGITUDE', 'NAV_LATITUDE']].iloc[::n].values.tolist()

    #every_nth_row_coordinates = coordinates

    geojson_line = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {}
            }
        ]
    }

    return geojson_line


def get_data_from_navlab(navlab_path, save_to_csv=False):
    df = navlab_trajectory(navlab_path)
    #print(df.head())
    version = navlab_path.parent.parent.name if navlab_path.parent and navlab_path.parent.parent else None
    if save_to_csv:
        df.to_csv(f"navlab{version}.csv", index=False)
        print(f"Wrote navlab{version}.csv")
    return df

def navigation_to_geojson(df):
    n=1 # Select only every n rows
    coordinates = df[['lon', 'lat']].iloc[::n].values.tolist()

    #every_nth_row_coordinates = coordinates

    geojson_line = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {}
            }
        ]
    }
    return geojson_line

def select_mission_folder():
    Tk().withdraw()

    mission_folder = askdirectory(title="Select missionfolder")
    if not mission_folder:
        print("No folder selected. Exiting.")
        return []
    return mission_folder

if __name__ == "__main__":    
    mission_folder_path = select_mission_folder()

    navp_trajectory_geojson = navp_trajectory(mission_folder_path)
    with open("navp_auv_path.geojson", 'w') as geojson_file:
        json.dump(navp_trajectory_geojson, geojson_file, indent=2)

    default_navlab, alternative_navlab = find_navlab_versions(mission_folder_path)
    for solution in alternative_navlab:
        version = solution.parent.parent.name if solution.parent and solution.parent.parent else None

        df = get_data_from_navlab(solution)
        nav_json = navigation_to_geojson(df)
        with open(f"navlab{version}.geojson", 'w') as geojson_file:
            json.dump(nav_json, geojson_file, indent=2)
