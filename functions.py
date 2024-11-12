#import packages and modules
import tkinter as tk
from tkinter import filedialog
import numpy as np
import rasterio
from rasterio.enums import Resampling
from osgeo import gdal, ogr, osr
import geopandas as gpd
from shapely.geometry import Point


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

    def load_fn(self, purpose):
        """this function opens a tkinter GUI for selecting a 
        file and returns the full path to the file 
        once selected
        
        'purpose' -- provides expanatory text in the GUI
        that tells the user what file to select"""

        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(title = purpose)

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
