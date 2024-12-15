import struct
import pandas as pd
from datetime import datetime, timezone
from typing import NamedTuple

# Module used to interpret binary navlab-solution.
# Joakim Skjefstad

class NavlabRow(NamedTuple):
    timestamp: float
    lat: float
    lon: float
    depth: float
    roll: float
    pitch: float
    heading: float
    vel_north: float
    vel_east: float
    vel_down: float
    std_lat: float
    std_lon: float
    std_depth: float
    cov_lat_lon: float
    std_roll: float
    std_pitch: float
    std_heading: float
    std_vel_north: float
    std_vel_east: float
    std_vel_down: float
    cov_vel_north_vel_east: float

bytes_per_row = 168 # bytes per row, navlab_smooth.bin has 168, 21 columns
number_of_doubles = str(round(bytes_per_row/8)) # 8 bytes per double (float), navlab_smooth.bin has 21 doubles

# Filepath to navlab_smooth.bin, list of columns to output, every nth row. Returns dataframe of selected values.
def read_navlab_smooth_to_dataframe(filepath, filter_columns, nth_row=10):
    print(f"Hang on... reading bin file, only every {nth_row} nth row")
    nav = []
    with open(filepath, "rb") as fp:
        while (data_bytes := fp.read(bytes_per_row)):
            row = NavlabRow._make(struct.unpack('<'+str(number_of_doubles)+'d', data_bytes))
            fp.seek((nth_row-1)*bytes_per_row, 1)
            #print_only(row)
            # attach row to table
            nav.append(row)

    # concatenate list of rows into a table
    nav_table = pd.DataFrame(nav)

    # timestamps to datetime
    print("Hang on... Calculating date & times and writting file")
    # timestamp is number of seconds since 1970-01-01
    # convert the timestamp to a datetime object (YMD HMS) in utc timezone
    # nav_table["datetime"] = [pd.Timestamp(s, unit='s', tz=timezone.utc).floor('S') for s in nav_table["timestamp"]  ]
    # this is a lot faster than pandas
    nav_table["datetime"] = [datetime.fromtimestamp(s,  tz=timezone.utc)  for s in nav_table["timestamp"] ] # .replace(microsecond=0)

    # select only some of the columns to save space
    # disable ( # ) this row if you want to export all the columns
    nav_table = nav_table[filter_columns]

    return nav_table


def main():
    print("Reading navlab_smooth.bin...")
    df = read_navlab_smooth_to_dataframe("navlab_smooth.bin", nth_row=10, filter_columns=["timestamp", "lat", "lon",  "depth"])
    df.to_csv("navlab_smooth.csv", index=False)
    print("Converted navlab_smooth.bin to navlab_smooth.csv, every 10th rows.")

if __name__=='__main__':
    main()
