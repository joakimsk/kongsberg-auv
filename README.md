# kongsberg-auv
Utilities to work with the Hugin and Munin AUV data output (missionfolders), navigation related.

## mp2geojson.py
Select mission-folder, will read mission-plan and create a geojson-object, showing the path in 2D that the AUV is planned to take.

## navp2geojson.py
Select mission-folder, will decimate navp (internal) navigation solution and create a geojson-object, showing the path in 2D that the AUV believes it took.

## pynavlab.py
Module to translate binary post-processed navlab_smooth.bin to dataframe/csv.

## navigation2geojson.py
Intended to convert both navp (internal) and postprocessed (navlab) alternatives. WIP.

## missiondir.py
Intended to be an interface to select a subset of folders from a mission-folder. WIP.

## Disclaimer
Not affiliated with Kongsberg or Kongsberg Discovery or anything else Kongsberg Group, but can be used to interpret their AUV datafiles.