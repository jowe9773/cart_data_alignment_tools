#import necessary packages and modules
import numpy as np
import rasterio
from rasterio.enums import Resampling
import matplotlib.pyplot as plt
from osgeo import gdal, ogr, osr
import geopandas as gpd
from shapely.geometry import Point
from functions import FileFunctions



ff = FileFunctions()

def plot_map(data, title, cmap="terrain"):
    plt.imshow(data, cmap=cmap)
    plt.colorbar()
    plt.title(title)
    plt.show()

def calculate_slope(elevation_array, transform):
    x, y = np.gradient(elevation_array, transform[0], transform[4])
    slope = np.sqrt(x**2 + y**2)
    slope_degrees = np.arctan(slope) * (180 / np.pi)
    return slope_degrees

def mask_by_slope(slope_data, threshold, replace_with_one=False):
    if replace_with_one:
        return np.where(slope_data > threshold, 1, np.nan)
    else:
        return np.where(slope_data > threshold, slope_data, np.nan)

# Step 1: Open the GeoTIFF and read elevation data
input_raster = ff.load_fn("Load sick geotiff")
with rasterio.open(input_raster) as src:
    elevation = src.read(1, resampling=Resampling.bilinear)
    transform = src.transform
    # Get the EPSG code from the raster metadata
    epsg_code = src.crs.to_epsg()

# Step 2: Calculate slope in degrees
slope = calculate_slope(elevation, transform)

# Step 3: Mask for slopes > 50 degrees
slope_mask_50 = mask_by_slope(slope, 50)

# Step 4: Calculate slope of masked > 50 layer
slope_of_mask_50 = calculate_slope(np.nan_to_num(slope_mask_50, nan=0), transform)

# Step 5: Mask for slopes > 20 on the new layer
final_mask_20 = mask_by_slope(slope_of_mask_50, 20, True)
final_mask_20 = final_mask_20.astype(np.uint8)

# Step 6: Polygonize final mask layer using GDAL
output_shapefile = input_raster.split(".")[0] + "_polygons.shp"

# Save final mask as a temporary raster to polygonize
driver = gdal.GetDriverByName("GTiff")
temp_raster = "temp_mask.tif"
with driver.Create(temp_raster, final_mask_20.shape[1], final_mask_20.shape[0], 1, gdal.GDT_Byte) as dst:
    dst.SetGeoTransform(transform.to_gdal())
    dst.SetProjection(f"EPSG:{epsg_code}")
    dst.GetRasterBand(1).WriteArray(final_mask_20)
    dst.GetRasterBand(1).SetNoDataValue(0)  # Set NoData value to 0 for areas outside the mask

    # Use GDAL Polygonize to create polygons from the mask layer
    src_band = dst.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)

    # Create shapefile for polygonized output
    driver = ogr.GetDriverByName("ESRI Shapefile")
    vector_dst = driver.CreateDataSource(output_shapefile)
    layer = vector_dst.CreateLayer("polygons", srs=srs, geom_type=ogr.wkbPolygon)
    field_defn = ogr.FieldDefn("value", ogr.OFTInteger)
    layer.CreateField(field_defn)

    # Perform polygonization
    gdal.Polygonize(src_band, src_band, layer, 0, [], callback=None)

    # Close datasets
    vector_dst.Destroy()
    dst = None

print("Polygonized shapefile created:", output_shapefile)

# Load the polygon shapefile
input_shapefile = input_raster.split(".")[0] + "_polygons.shp"
gdf = gpd.read_file(input_shapefile)

# Calculate area and add as a new column (assumes the CRS is in meters)
gdf['area'] = gdf.geometry.area

# Define area thresholds
min_area = 100  # Replace with your minimum area threshold
max_area = 400  # Replace with your maximum area threshold

# Filter polygons by area
filtered_gdf = gdf[(gdf['area'] >= min_area) & (gdf['area'] <= max_area)]

# Save the filtered polygons to a new shapefile
output_filtered_shapefile = input_raster.split(".")[0] + "_filtered_polygons.shp"
filtered_gdf.to_file(output_filtered_shapefile)

print("Filtered shapefile created:", output_filtered_shapefile)

# Load the filtered polygon shapefile
filtered_shapefile = input_raster.split(".")[0] + "_filtered_polygons.shp"
gdf = gpd.read_file(filtered_shapefile)

# Function to create minimum bounding circle
def minimum_bounding_circle(polygon):
    centroid = polygon.centroid
    # Calculate the maximum distance from the centroid to any point on the boundary
    radius = max(centroid.distance(Point(coords)) for coords in polygon.exterior.coords)
    # Create a circular geometry from the centroid and radius
    circle = centroid.buffer(radius)
    return circle

# Apply function to each geometry in the GeoDataFrame
gdf['min_bounding_circle'] = gdf.geometry.apply(minimum_bounding_circle)

# Convert bounding circles to a new GeoDataFrame
circle_gdf = gpd.GeoDataFrame(gdf[['min_bounding_circle']], geometry='min_bounding_circle', crs=gdf.crs)

# Save the circles to a new shapefile
output_circle_shapefile = input_raster.split(".")[0] + "_bounding_circles.shp"
circle_gdf.to_file(output_circle_shapefile)

print("Minimum bounding circle shapefile created:", output_circle_shapefile)

# Load the polygon shapefile
input_shapefile = input_raster.split(".")[0] + "_bounding_circles.shp"
gdf = gpd.read_file(input_shapefile)

# Calculate area and add as a new column (assumes the CRS is in meters)
gdf['area'] = gdf.geometry.area

# Define area thresholds
min_area = 100  # Replace with your minimum area threshold
max_area = 400  # Replace with your maximum area threshold

# Filter polygons by area
filtered_gdf = gdf[(gdf['area'] >= min_area) & (gdf['area'] <= max_area)]

# Save the filtered polygons to a new shapefile
output_filtered_shapefile = input_raster.split(".")[0] + "_filtered_mbc.shp"
filtered_gdf.to_file(output_filtered_shapefile)

print("Filtered shapefile created:", output_filtered_shapefile)

# Calculate centroids
filtered_gdf['centroid'] = filtered_gdf.geometry.centroid

# Create a new GeoDataFrame for the centroids
centroid_gdf = gpd.GeoDataFrame(filtered_gdf[['centroid']], geometry='centroid', crs=filtered_gdf.crs)

# Save the centroids to a new shapefile
output_centroid_shapefile = input_raster.split(".")[0] + "_centroids.shp"
centroid_gdf.to_file(output_centroid_shapefile)

print("Centroid shapefile created:", output_centroid_shapefile)