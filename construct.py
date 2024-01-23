
import os
import csv
import shutil
import arcpy
import googlemaps
from libs.elevation import *

# longitude: start,end,step
lng = (119.9, 122.05, 0.05)
# latitude:  start,end,step
lat = (21.8, 25.35, 0.05)
# save elevation results
save = True
# google map api configuration
gmaps = googlemaps.Client(key='your api key here') 
# add the following argument if a proxy is needed to visit google
# requests_kwargs={'proxies':{"http":"http://localhost:7890","https":"http://localhost:7890"}}

# maxnum: max points in single request 
elevations = request_elevation(gmaps, lng, lat, maxnum=512)

cur = None
OUTPUT_PATH = os.path.join(os.getcwd(), "output")
GDB_PATH = os.path.join(OUTPUT_PATH, "DEM.gdb")
PNT_PATH = os.path.join(GDB_PATH, "ELEVATION_POINTS")
TIN_PATH = os.path.join(OUTPUT_PATH, "TIN")
DEM_PATH = os.path.join(GDB_PATH, "DEM")
CSV_PATH = os.path.join(OUTPUT_PATH, "Elevations.csv")
SPAT_REF = arcpy.SpatialReference(4326)

try:
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    os.mkdir(OUTPUT_PATH)

    arcpy.management.CreateFileGDB(
        os.path.dirname(GDB_PATH),
        os.path.basename(GDB_PATH))
    
    # Create the output feature class and add elevation field
    arcpy.management.CreateFeatureclass(
        os.path.dirname(PNT_PATH),
        os.path.basename(PNT_PATH), 
        "POINT", 
        spatial_reference = SPAT_REF
    )
    arcpy.management.AddField(
        PNT_PATH, 
        "Elevation", 
        "DOUBLE"
    ) 
    
    # Open the feature cusor
    cur = arcpy.da.InsertCursor(PNT_PATH, ["SHAPE@X", "SHAPE@Y", "Elevation"])
    
    # Write points
    if save:
        with open(CSV_PATH, "w") as fd:
            c = csv.writer(fd)
            for loc in elevations:
                for subloc in loc:
                    x, y = subloc['location']['lng'], subloc['location']['lat']
                    elevation = subloc['elevation']
                    c.writerow([x, y, elevation])
                    cur.insertRow([x, y, elevation])       
    else:
        for loc in elevations:
            for subloc in loc:
                x, y = subloc['location']['lng'], subloc['location']['lat']
                elevation = subloc['elevation']
                cur.insertRow([x, y, elevation])

except Exception as e:
    print(e)
finally:
    # Clean up the cursor if necessary
    if cur:
        del cur 

try:
    arcpy.ddd.CreateTin(
        out_tin = TIN_PATH, 
        spatial_reference = SPAT_REF, 
        in_features = [[PNT_PATH, "Elevation", "Mass_Points", "<None>"]],
        constrained_delaunay = "constrained_delaunay"
    )
    arcpy.ddd.TinRaster(
        TIN_PATH, 
        DEM_PATH
    )
except Exception as e:
    print(e)