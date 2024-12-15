# Import necessary libraries
import geopandas as gpd
import os
from scipy.spatial.distance import cdist
from osgeo import gdal
from pprint import pprint
from functions import FileFunctions
from functions import FindPairsFunctions

# Initialize FileFunctions for file selection
ff = FileFunctions()
fpf = FindPairsFunctions()

# Step 1a: Choose files
scan1 = ff.load_fn("Select reference scan", [("Centroid Files", "*_centroids.shp")])
scan2 = ff.load_fn("Select a second scan", [("Centroid Files", "*_centroids.shp")])

# Step 1b: Set up filename parts for future use
directory1, filename1 = os.path.split(scan1)
basename1 = filename1.split("_centroids")[0]

directory2, filename2 = os.path.split(scan2)
basename2 = filename2.split("_centroids")[0]

# Step 1c: Choose a directory to look for GeoTIFF files
geotif_location = ff.load_dn("Choose a directory with GeoTIFF files")
geotif2 = geotif_location+ "/" + basename2 + ".tif"

#Step 1d: Choose an output location
output_location = ff.load_dn("Choose output directory")
output = output_location + "/" + basename2 + ".tif"
print(output)


#Step 2: Find pairs
pairs = fpf.find_closest_pairs(scan1, scan2)
pprint(pairs)

#Step 3: Convert Pairs to gdal GCPS
gcps = fpf.pairs_to_gcps(pairs, geotif2)

#Step 4: Tranform scan2 using gcps
fpf.transform_scan2(geotif2, gcps, output)  