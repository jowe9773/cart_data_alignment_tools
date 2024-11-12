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

def polygonize_mask(mask_array, transform, epsg_code, output_shapefile):
    driver = gdal.GetDriverByName("GTiff")
    temp_raster = "temp_mask.tif"
    
    with driver.Create(temp_raster, mask_array.shape[1], mask_array.shape[0], 1, gdal.GDT_Byte) as dst:
        dst.SetGeoTransform(transform.to_gdal())
        dst.SetProjection(f"EPSG:{epsg_code}")
        dst.GetRasterBand(1).WriteArray(mask_array)
        dst.GetRasterBand(1).SetNoDataValue(0)
        
        src_band = dst.GetRasterBand(1)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg_code)
        
        driver = ogr.GetDriverByName("ESRI Shapefile")
        vector_dst = driver.CreateDataSource(output_shapefile)
        layer = vector_dst.CreateLayer("polygons", srs=srs, geom_type=ogr.wkbPolygon)
        field_defn = ogr.FieldDefn("value", ogr.OFTInteger)
        layer.CreateField(field_defn)
        
        gdal.Polygonize(src_band, src_band, layer, 0, [], callback=None)
        
        vector_dst.Destroy()

def filter_by_area(geodataframe, min_area, max_area, output_shapefile):
    filtered_gdf = geodataframe[(geodataframe['area'] >= min_area) & (geodataframe['area'] <= max_area)]
    filtered_gdf.to_file(output_shapefile)
    return filtered_gdf

def minimum_bounding_circle(polygon):
    centroid = polygon.centroid
    radius = max(centroid.distance(Point(coords)) for coords in polygon.exterior.coords)
    return centroid.buffer(radius)

def process_raster(input_raster, min_area=100, max_area=400):
    # Load the GeoTIFF
    with rasterio.open(input_raster) as src:
        elevation = src.read(1, resampling=Resampling.bilinear)
        transform = src.transform
        epsg_code = src.crs.to_epsg()

    # Step 2: Calculate slope in degrees
    slope = calculate_slope(elevation, transform)

    # Step 3: Mask for slopes > 50 degrees
    slope_mask_50 = mask_by_slope(slope, 50)

    # Step 4: Calculate slope of masked > 50 layer
    slope_of_mask_50 = calculate_slope(np.nan_to_num(slope_mask_50, nan=0), transform)

    # Step 5: Mask for slopes > 20 on the new layer
    final_mask_20 = mask_by_slope(slope_of_mask_50, 20, True).astype(np.uint8)

    # Step 6: Polygonize final mask layer
    output_shapefile = input_raster.split(".")[0] + "_polygons.shp"
    polygonize_mask(final_mask_20, transform, epsg_code, output_shapefile)
    print("Polygonized shapefile created:", output_shapefile)

    # Step 7: Load polygon shapefile and filter by area
    gdf = gpd.read_file(output_shapefile)
    gdf['area'] = gdf.geometry.area
    filtered_gdf = filter_by_area(gdf, min_area, max_area, output_shapefile.replace(".shp", "_filtered.shp"))
    print("Filtered shapefile created:", output_shapefile.replace(".shp", "_filtered.shp"))

    return filtered_gdf

def create_bounding_circles(geodataframe, output_shapefile):
    geodataframe['min_bounding_circle'] = geodataframe.geometry.apply(minimum_bounding_circle)
    circle_gdf = gpd.GeoDataFrame(geodataframe[['min_bounding_circle']], geometry='min_bounding_circle', crs=geodataframe.crs)
    circle_gdf.to_file(output_shapefile)
    print("Minimum bounding circle shapefile created:", output_shapefile)

def calculate_centroids(geodataframe, output_shapefile):
    geodataframe['centroid'] = geodataframe.geometry.centroid
    centroid_gdf = gpd.GeoDataFrame(geodataframe[['centroid']], geometry='centroid', crs=geodataframe.crs)
    centroid_gdf.to_file(output_shapefile)
    print("Centroid shapefile created:", output_shapefile)

# Main processing flow
input_raster = ff.load_fn("Load sick geotiff")
filtered_polygons = process_raster(input_raster)

# Create bounding circles for filtered polygons
bounding_circle_shapefile = input_raster.split(".")[0] + "_bounding_circles.shp"
create_bounding_circles(filtered_polygons, bounding_circle_shapefile)

# Calculate centroids of bounding circles
centroid_shapefile = input_raster.split(".")[0] + "_centroids.shp"
calculate_centroids(filtered_polygons, centroid_shapefile)
