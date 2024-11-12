# process to find centers
import numpy as np
import geopandas as gpd
from functions import FileFunctions, FindCentersFunctions

ff = FileFunctions()
fcf = FindCentersFunctions()

#load raster
sick_file = ff.load_fn("Choose a sick scan to find centers of")
scan = fcf.load_raster(sick_file)

#select output directory
out_dir = ff.load_dn("Select output directory")
out_filename_no_suffix = out_dir + "/" + sick_file.split(".")[0].split("/")[-1]


#process to find center of holes on floodplain
#find slope
slope = fcf.calculate_slope(scan[0], scan[1])

#mask slope so only areas of slopes greater than 50 are saved
high_slope_mask = fcf.mask_by_slope(slope, 50, False)

#find the slope of the mask to find the edges of the high slope areas
slope_of_high_slope_mask = fcf.calculate_slope(np.nan_to_num(high_slope_mask, nan=0), scan[1])

#mask to only find areas of high slope change
final_mask = fcf.mask_by_slope(slope_of_high_slope_mask, 20, True).astype(np.uint8)

#convert to polygons
polygons_file = out_filename_no_suffix + "_polygons.shp"
fcf.polygonize_mask(final_mask, scan[1], scan[2], polygons_file)

#filter polygons to a particular size
gdf = gpd.read_file(polygons_file)
gdf['area'] = gdf.geometry.area
filtered_gdf = fcf.filter_by_area(gdf, 100, 400, polygons_file)

#find bounding circles of the filtered polygons
bounding_circles_file = out_filename_no_suffix + "_bounding_circles.shp"
fcf.create_bounding_circles(filtered_gdf, bounding_circles_file)

#filter bounding circles to a particular size (same range as polygons)
gdf = gpd.read_file(bounding_circles_file)
print(gdf)
gdf['area'] = gdf.geometry.area
filtered_gdf = fcf.filter_by_area(gdf, 100, 400, bounding_circles_file)

#find centroids of bounding circles
centroids_file = out_filename_no_suffix + "_centroids.shp"
fcf.calculate_centroids(filtered_gdf, centroids_file)
