"""Import neccesary packages and modules"""
import pandas as pd
import numpy as np
from osgeo import gdal
import os
from functions import FileFunctions, FindPairsFunctions

"""Instantiate classes"""
ff = FileFunctions()
fpf = FindPairsFunctions()

"""prepare GDAL for use"""
gdal.UseExceptions()

"""Load centroid files"""
reference_centroids = ff.load_fn("Load reference scan centroids (should be a wood scan)", [("Centroid Shapefiles", "*centroids.shp")])
misaligned_centroids = ff.load_fn("Load reference scan centroids (should be either a nowood or remobilization scan)", [("Centroid Shapefiles", "*centroids.shp")])

"""Find pairs and prep them for use as GCPs"""
#find closest pairs in data
pairs = fpf.find_closest_pairs(reference_centroids, misaligned_centroids)
print(pairs)

# Flatten the tuples and create columns
flat_data = []
for (ref_x, ref_y), (mis_x, mis_y) in pairs:
    flat_data.append([ref_x, ref_y, mis_x, mis_y])

# Create DataFrame
pairs_df = pd.DataFrame(flat_data, columns=["ReferenceX", "ReferenceY", "MisalignedX", "MisalignedY"])

# Calculate offsets
offsets = fpf.calculate_offsets(pairs)

# Convert the NumPy array to a DataFrame and append it
new_df = pd.DataFrame(offsets, columns=["OffX", "OffY"])

# Append new columns to the original DataFrame
pairs_df = pd.concat([pairs_df, new_df], axis=1)

pairs_df['Offset'] = np.sqrt(pairs_df['OffX']**2 + pairs_df['OffY']**2)

# Filter the rows where the absolute value of 'Offset' is no larger than 20
filtered_df = pairs_df[pairs_df['Offset'] <= 20]

print(filtered_df)

"""Load scan files"""
misaligned_scan = ff.load_fn("Load misaligned scan (should be either a nowood or remobilization scan)", [("TIF files", "*.tif")])
output_location = ff.load_dn("Select an output directory")
output_tiff = output_location + "/" + os.path.basename(misaligned_scan).split(".")[0] + "_aligned.tif"

"""Apply the GCP points and align the misaligned scan with the reference scan"""
# Open the input GeoTIFF
misaligned_ds = gdal.Open(misaligned_scan, gdal.GA_ReadOnly)


# Create a copy of the input file
misaligned_copy_tif = output_location + "/" + os.path.basename(misaligned_scan)
gdal.Translate(misaligned_copy_tif, misaligned_ds)

# Clean up
misaligned_ds = None

#open misaligned topo copy
src_ds = gdal.Open(misaligned_copy_tif, gdal.GA_ReadOnly)

# Get the GeoTransform and projection from the input dataset
geo_transform = src_ds.GetGeoTransform()
print(geo_transform)
projection = src_ds.GetProjection()

# Calculate pixel/line (pixel_x, pixel_y) from real-world coordinates using GeoTransform
filtered_df['pixel'] = (filtered_df['MisalignedX'] - geo_transform[0]) / geo_transform[1]
filtered_df['line'] = (filtered_df['MisalignedY'] - geo_transform[3]) / geo_transform[5]

# Create a list of GCPs from the DataFrame
gcps = [
    gdal.GCP(row['ReferenceX'], row['ReferenceY'], 0, row['pixel'], row['line'])
    for _, row in filtered_df.iterrows()
]


# Assign GCPs to the dataset
# Here we use the projection from the original image, but you can change it if needed
src_ds.SetGCPs(gcps, src_ds.GetProjection())

# Apply the transformation and create a new GeoTIFF (Ensure original file is not altered)
gdal.Warp(
    output_tiff,        # Output file path
    src_ds,             # Source dataset
    format="GTiff",     # Output format    
    dstSRS="EPSG:32615",  # Target spatial reference system (adjust as needed)
    transformerOptions = ["SRC_METHOD=GCP_POLYNOMIAL"]
)

# Clean up and close the datasets, delete copy we were working off of
src_ds = None
os.remove(misaligned_copy_tif)