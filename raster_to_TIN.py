import numpy as np
import rasterio
from matplotlib import pyplot as plt
from rasterio.enums import Resampling
import plotly.graph_objs as go
from functions import FileFunctions

ff = FileFunctions()

#load tif file
geotiff_path = ff.load_fn("Choose a tif file")

# Open the GeoTIFF file using rasterio
with rasterio.open(geotiff_path) as src:
    # Read the image data
    img_data = src.read(1)  # Read the first band, for multi-band GeoTIFFs, you can specify other band numbers
    geotransform = src.transform # Get geotransform information


# Plot the image using matplotlib
plt.imshow(img_data, cmap='viridis')  # You can change the colormap as needed
plt.colorbar()  # Optionally add a colorbar
plt.title('GeoTIFF Image')
plt.show()

def calculate_slope(elevation_array, transform):
    x, y = np.gradient(elevation_array, transform[0], transform[4])
    slope = np.sqrt(x**2 + y**2)
    slope_degrees = np.arctan(slope) * (180 / np.pi)
    return slope_degrees

slope = calculate_slope(img_data, geotransform)

# Plot the slope using matplotlib
plt.imshow(slope, cmap='viridis')  # You can change the colormap as needed
plt.colorbar()  # Optionally add a colorbar
plt.title('GeoTIFF slope')
plt.show()

def mask_by_slope(slope_data, threshold, replace_with_one=False):
    if replace_with_one:
        return np.where(slope_data > threshold, 1, np.nan)
    else:
        return np.where(slope_data > threshold, slope_data, np.nan)
    
#mask slope to get areas of high slope
high_slope = mask_by_slope(slope, 40, True)

# Plot the slope using matplotlib
plt.imshow(high_slope, cmap='viridis')  # You can change the colormap as needed
plt.colorbar()  # Optionally add a colorbar
plt.title('High Slope Mask')
plt.show()

# Get the indices where mask is 1 (ignoring NaN values)
indices = np.where(high_slope == 1)

# Convert indices (x, y) to real-world coordinates using the geotransform
result = []
for x, y in zip(*indices):
    # Apply the geotransform to convert to real-world coordinates
    real_world_x, real_world_y = geotransform * (x, y)
    
    # Get the elevation value from the elevation data
    elevation = img_data[x, y]
    
    # Append the result as (real_world_x, real_world_y, elevation)
    result.append((real_world_x, real_world_y, elevation))

print(result)
