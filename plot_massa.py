import rasterio
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from functions import FileFunctions

# Load CSV data as you were doing before
ff = FileFunctions()

file_path = ff.load_fn("Select your csv file", [("CSV files", "*.CSV"), ("All Files", "*.*")])
df = pd.read_csv(file_path, skiprows=29, usecols=[0, 2, 3, 5], header=None)
df.columns = ['Dataset', 'X', 'Y', 'Z']

file_path_channel = ff.load_fn("Select your csv file", [("CSV files", "*.CSV"), ("All Files", "*.*")])
df_channel = pd.read_csv(file_path_channel, skiprows=29, usecols=[2, 3, 5], header=None)
df_channel.columns = ['X', 'Y', 'Z']
df_channel["Dataset"] = 6

df_combined = pd.concat([df, df_channel], ignore_index=True)

# Load tif file
geotiff_path = ff.load_fn("Choose a tif file")

# Open the GeoTIFF file using rasterio
with rasterio.open(geotiff_path) as src:
    # Read the image data
    img_data = src.read(1)  # Read the first band, for multi-band GeoTIFFs, you can specify other band numbers
    geotransform = src.transform  # Get geotransform information

    # Calculate the coordinates corresponding to the pixels
    rows, cols = img_data.shape
    y_coords = np.arange(0, cols, 10)  # Select every 10th column
    x_coords = np.arange(0, rows, 10)  # Select every 10th row

    x_list = []
    y_list = []
    z_list = []

    for x in x_coords:
        for y in y_coords:
            print(x, y)
            # Apply the geotransform to convert to real-world coordinates
            real_world_x, real_world_y = geotransform * (y, x)
            
            # Get the elevation value from the elevation data
            elevation = img_data[x, y]
            
            # Append the result as (real_world_x, real_world_y, elevation)
            x_list.append(real_world_x)
            y_list.append(real_world_y)
            z_list.append(elevation)

# Create a DataFrame with the extracted points
df_geotiff = pd.DataFrame({
    'X': x_list,
    'Y': y_list,
    'Z': z_list
})

df_geotiff["Dataset"] = 7

# Merge the extracted GeoTIFF points with your CSV data if needed
df_combined = pd.concat([df_combined, df_geotiff], ignore_index=True)


# Create a 3D scatter plot with the combined data
fig = go.Figure()

# Plot the scatter data
for dataset, group in df_combined.groupby('Dataset'):
    # Customize marker size and color for dataset 7
    if dataset == 7:
        marker_settings = dict(size=1, color='black')
    else:
        marker_settings = dict(size=5)  # Default for datasets 1-6
    
    fig.add_trace(go.Scatter3d(
        x=group['X'],
        y=group['Y'],
        z=group['Z'],
        mode='markers',
        marker=marker_settings,
        name=f'Dataset {dataset}'
    ))

fig.show()