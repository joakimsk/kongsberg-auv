import pandas as pd
import geojson
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory
import re

# mp2geojson.py
# Reads a HuginOS missionplan .mp and does its best to output a geojson-object of the path planned.
# Joakim Skjefstad

def create_geojson_point(row):
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        return geojson.Point((row['Longitude'], row['Latitude']))
    return None

def dmm_to_decimal(degrees, minutes, direction):
    decimal = degrees + (minutes / 60)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

# Function to check if a string matches the Degrees:Minutes.decimalminutesDirection format
def is_valid_dmm(value):
    # Regular expression to match the format Degrees:Minutes.decimalminutesDirection
    pattern = r"^\d{1,3}:\d{1,2}(\.\d+)?[NSWE]$"
    return bool(re.match(pattern, value))

def parse_lat_lon(lat_lon_str):
    match = re.match(r"(\d+):(\d+\.\d+)([NSEW])", lat_lon_str)
    if not match:
        raise ValueError(f"Invalid latitude/longitude format: {lat_lon_str}")
    degrees = int(match.group(1))
    minutes = float(match.group(2))
    direction = match.group(3)
    return dmm_to_decimal(degrees, minutes, direction)

def read_missionplan(mission_folder_path: Path):
    mission_name = mission_folder_path.name
    mission_plan_path = mission_folder_path / Path("mission.mp")
 
    waypoint_lines = []
    with open(mission_plan_path, 'r') as file:
        for line in file:
            if line.startswith(":"):  # Extract waypoint lines
                waypoint_lines.append(line.strip())

    columns = ["Tag", "Depth", "Alt", "DMo", "Latitude", "Longitude", "Course", "GMo", "Speed", "SMo", "Dur", "Dist", "Flags"]
    
    df = pd.DataFrame(columns=columns)


    for idx, line in enumerate(waypoint_lines):
        # Split the line based on whitespace, accounting for varying spaces
        fields = re.split(r'\s+', line[1:])  # Remove leading ':'
        if len(fields) >= 10:  # Ensure enough fields are present to extract data
            Tag = fields[0]
            Depth = fields[1]
            Alt = fields[2]
            DMo = fields[3]
            Latitude = fields[4]
            Longitude = fields[5]
            Course = fields[6]
            GMo = fields[7]
            Speed = fields[8]
            SMo = fields[9]
            Dur = fields[10]
            Dist = fields[11]
            try:
                Flags = fields[12]
            except: # No flags found, set to None
                Flags = None

            new_wp = {
                "Tag": Tag, "Depth": Depth, "Alt": Alt, "DMo": DMo, "Latitude": Latitude, 
                "Longitude": Longitude, "Course": Course, "GMo": GMo, "Speed": Speed, "SMo": SMo, 
                "Dur": Dur, "Dist": Dist, "Flags": Flags
            }

            df = pd.concat([df, pd.DataFrame([new_wp])], ignore_index=True)

    #print(df)
    
    # If a valid latitude longitude pair is found, convert it to decimal degrees
    df['Latitude'] = df['Latitude'].apply(lambda x: parse_lat_lon(x) if is_valid_dmm(x) else None)
    df['Longitude'] = df['Longitude'].apply(lambda x: parse_lat_lon(x) if is_valid_dmm(x) else None)

    #print(df)


    points = []
    for _, row in df.iterrows():
        point = create_geojson_point(row)
        if point:
            # Add properties like "tag"
            point_with_properties = geojson.Feature(geometry=point, properties={"tag": row['Tag']})
            points.append(point_with_properties)

    # Create a LineString from all valid points
    coordinates = [(row['Longitude'], row['Latitude']) for _, row in df.iterrows() if pd.notna(row['Latitude']) and pd.notna(row['Longitude'])]
    linestring = geojson.LineString(coordinates)

    # Create a FeatureCollection containing the points and the linestring
    feature_collection = geojson.FeatureCollection(points + [geojson.Feature(geometry=linestring)])

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
    print(f"Reading {mission_name} and making geojson-file.")
    
    mp_geojson = read_missionplan(mission_folder_path)
    output_filename = f"{mission_name}_missionplan.geojson"
    with open(output_filename, 'w') as geojson_file:
        geojson.dump(mp_geojson, geojson_file, indent=2)
        print(f"Wrote {output_filename} successfully.")
