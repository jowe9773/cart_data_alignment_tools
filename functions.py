#import packages and modules
import tkinter as tk
from tkinter import filedialog
import numpy as np
import rasterio
from rasterio.enums import Resampling
from osgeo import gdal, ogr, osr
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial.distance import cdist
import os

class FileFunctions:
    """Class contains methods for managing files"""

    def __init__(self):
        print("Initialized file managers")

    def load_dn(self, purpose):
        """this function opens a tkinter GUI for selecting a 
        directory and returns the full path to the directory 
        once selected
        
        'purpose' -- provides expanatory text in the GUI
        that tells the user what directory to select"""

        root = tk.Tk()
        root.withdraw()
        directory_name = filedialog.askdirectory(title = purpose)

        return directory_name

    def load_fn(self, purpose, types = [("All files", "*.*")]):
        """this function opens a tkinter GUI for selecting a 
        file and returns the full path to the file 
        once selected
        
        'purpose' -- provides expanatory text in the GUI
        that tells the user what file to select
        
        'filetypes' -- allows you to select particular file types to look for"""

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(title = purpose, filetypes = types)

        return filename
    
class FindCentersFunctions:
    def __init__(self):
        print("Initialized Find Centers Functions")

    def load_raster(self, input_raster):
        with rasterio.open(input_raster) as src:
            elevation = src.read(1, resampling=Resampling.bilinear)
            transform = src.transform
            epsg_code = src.crs.to_epsg()
            raster_info = [elevation, transform, epsg_code]
        
        return raster_info

    def calculate_slope(self, elevation_array, transform):
        x, y = np.gradient(elevation_array, transform[0], transform[4])
        slope = np.sqrt(x**2 + y**2)
        slope_degrees = np.arctan(slope) * (180 / np.pi)
        return slope_degrees

    def mask_by_slope(self, slope_data, threshold, replace_with_one=False):
        if replace_with_one:
            return np.where(slope_data > threshold, 1, np.nan)
        else:
            return np.where(slope_data > threshold, slope_data, np.nan)

    def polygonize_mask(self, mask_array, transform, epsg_code, output_shapefile):
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

    def filter_by_area(self, geodataframe, min_area, max_area, output_shapefile):
        filtered_gdf = geodataframe[(geodataframe['area'] >= min_area) & (geodataframe['area'] <= max_area)]
        filtered_gdf.to_file(output_shapefile)
        return filtered_gdf

    def create_bounding_circles(self, geodataframe, output_shapefile):

        def minimum_bounding_circle(polygon):
            centroid = polygon.centroid
            radius = max(centroid.distance(Point(coords)) for coords in polygon.exterior.coords)
            return centroid.buffer(radius)

        geodataframe['min_bounding_circle'] = geodataframe.geometry.apply(minimum_bounding_circle)
        circle_gdf = gpd.GeoDataFrame(geodataframe[['min_bounding_circle']], geometry='min_bounding_circle', crs=geodataframe.crs)
        circle_gdf.to_file(output_shapefile)
        print("Minimum bounding circle shapefile created:", output_shapefile)

    def calculate_centroids(self, geodataframe, output_shapefile):
        geodataframe['centroid'] = geodataframe.geometry.centroid
        centroid_gdf = gpd.GeoDataFrame(geodataframe[['centroid']], geometry='centroid', crs=geodataframe.crs)
        centroid_gdf.to_file(output_shapefile)
        print("Centroid shapefile created:", output_shapefile)

class FindPairsFunctions:

    def __init__(self):
        print("Initialized FindPairFunctions")

    def find_closest_pairs(self, scan1, scan2):
        shapefile_1 = gpd.read_file(scan1)
        shapefile_2 = gpd.read_file(scan2)

        # Ensure both shapefiles use the same CRS
        if shapefile_1.crs != shapefile_2.crs:
            print("CRS does not match")
            shapefile_2 = shapefile_2.to_crs(shapefile_1.crs)

        # Extract the points (coordinates) from both shapefiles
        points_1 = shapefile_1.geometry.apply(lambda x: (x.x, x.y)).tolist()
        points_2 = shapefile_2.geometry.apply(lambda x: (x.x, x.y)).tolist()

        # Step 3: Calculate pairwise distances between points
        distances = cdist(points_1, points_2)

        # Find the closest point pairs
        closest_pairs = []
        for i in range(len(points_1)):
            closest_index = distances[i].argmin()
            closest_pairs.append((points_1[i], points_2[closest_index]))

        return closest_pairs
    
    def pairs_to_gcps(self, point_pairs, geotiff_location):
        # Function to convert real-world coordinates to pixel coordinates
        def geo_to_pixel(geo_x, geo_y, geo_transform):
            top_left_x = geo_transform[0]
            pixel_width = geo_transform[1]
            top_left_y = geo_transform[3]
            pixel_height = geo_transform[5]
            
            # Calculate pixel coordinates (row, column)
            pixel_x = (geo_x - top_left_x) / pixel_width
            pixel_y = (geo_y - top_left_y) / pixel_height
            
            return pixel_x, pixel_y
        
        
        # Open the geotiff for the second scan (scan we are going to transform)
        scan2_ds = gdal.Open(geotiff_location)

        # Get the GeoTransform of scan2 and extract parameters
        geo_transform = scan2_ds.GetGeoTransform()
        top_left_x = geo_transform[0]
        pixel_width = geo_transform[1]
        top_left_y = geo_transform[3]
        pixel_height = geo_transform[5]

        # Create a list to hold GCPs
        gcp_list = []

        # Convert all the scan2 real-world coordinates to pixel locations and create GCPs
        for pair in point_pairs:
            # Get the real-world coordinates of scan2
            (scan1_x, scan1_y), (scan2_x, scan2_y) = pair
            
            # Convert to pixel coordinates
            pixel_x, pixel_y = geo_to_pixel(scan2_x, scan2_y, geo_transform)
            
            # Create GCP (geo_x, geo_y, geo_z, pixel_x, pixel_y)
            gcp = gdal.GCP(scan1_x, scan1_y, 0, pixel_x, pixel_y)
            
            # Append the GCP to the list
            gcp_list.append(gcp)

        return gcp_list

    def transform_scan2(self, scan2_filename, gcps_list, output_filename):
        #Open scan 2
        scan2_dataset = gdal.Open(scan2_filename)

        # Create a new dataset to avoid modifying the original scan2_ds
        driver = gdal.GetDriverByName('GTiff')
        output_ds = driver.Create("scan2_with_gcps.tif", scan2_dataset.RasterXSize, scan2_dataset.RasterYSize,
                          scan2_dataset.RasterCount, gdal.GDT_Float32)
        
        # Copy the original data to the new file (output_ds)
        for i in range(scan2_dataset.RasterCount):
            output_ds.GetRasterBand(i + 1).WriteArray(scan2_dataset.GetRasterBand(i + 1).ReadAsArray())

        # Set the projection and GCPs to the new output dataset
        output_ds.SetProjection(scan2_dataset.GetProjection())
        output_ds.SetGCPs(gcps_list, scan2_dataset.GetProjection())

        # Close datasets
        scan2_ds = None  # Close the original dataset
        output_ds = None  # Close the new dataset with GCPs

        # Open the dataset that contains GCPs
        scan2_with_gcps_ds = gdal.Open("scan2_with_gcps.tif")
        # Get the projection (SRS) from scan2_ds
        source_srs = scan2_with_gcps_ds.GetProjection()

        # Create the GDAL warp options explicitly
        warp_options = gdal.WarpOptions(
            format="GTiff"              # Output format (GeoTIFF)
        )

        # Perform the transformation (warping) based on the same SRS and options
        reprojected_ds = gdal.Warp(output_filename, scan2_with_gcps_ds, options=warp_options)

        print(reprojected_ds)

        # Close the datasets
        scan2_with_gcps_ds = None
        reprojected_ds = None

        # Delete the temporary scan2_with_gcps.tif file
        os.remove("scan2_with_gcps.tif")
