from osgeo import gdal
from osgeo.gdal import DEMProcessingOptions
from functions import FileFunctions


ff = FileFunctions()

# Input and output file paths
input_file = ff.load_fn("Load input file to dilate to erode", [("Geotiffs", "*.TIF"), ("All Files", "*.*")])
output_dest = ff.load_dn("Choose place to store outputs")
output_file_dilate = output_dest + "/dilated.tif"
output_file_erode = output_dest + "/eroded.tif"

gdal.UseExceptions()
print(f"GDAL version: {gdal.VersionInfo()}")

# Open the input raster file
src_ds = gdal.Open(input_file)

if not src_ds:
    raise ValueError("Input raster could not be opened. Check the file path and format.")
print(f"Raster successfully opened: {input_file}")
print(f"Raster bands: {src_ds.RasterCount}")
print(f"Raster size: {src_ds.RasterXSize}x{src_ds.RasterYSize}")

