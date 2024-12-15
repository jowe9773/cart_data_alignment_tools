import rasterio
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from functions import FileFunctions
from scipy.spatial import Delaunay

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

# Load the GeoTIFF file
file_path_geotiff = ff.load_fn("Select your GeoTIFF file", [("GeoTIFF files", "*.tif"), ("All Files", "*.*")])

# Read the elevation data from the GeoTIFF file
with rasterio.open(file_path_geotiff) as src:
    elevation_data = src.read(1)  # Reading the first band of the GeoTIFF file (assumed to be the elevation data)
    transform = src.transform

# Get the dimensions of the GeoTIFF
rows, cols = elevation_data.shape

# Get the x and y coordinates from the GeoTIFF file
x_coords, y_coords = np.meshgrid(
    np.arange(cols) * transform[0] + transform[2],  # Calculate x coordinates
    np.arange(rows) * transform[4] + transform[5]   # Calculate y coordinates
)

# Flatten the x, y, and z data for triangulation
x_flat = x_coords.flatten()
y_flat = y_coords.flatten()
z_flat = elevation_data.flatten()

# Remove NaN values (if any) from the flattened arrays
valid_indices = ~np.isnan(z_flat)
x_flat = x_flat[valid_indices]
y_flat = y_flat[valid_indices]
z_flat = z_flat[valid_indices]

# Perform Delaunay triangulation
points = np.vstack([x_flat, y_flat]).T  # Create a 2D array of x and y coordinates
triangulation = Delaunay(points)  # Perform the triangulation

# Create a 3D scatter plot
fig = go.Figure()

# Plot the scatter data
for dataset, group in df_combined.groupby('Dataset'):
    fig.add_trace(go.Scatter3d(
        x=group['X'],
        y=group['Y'],
        z=group['Z'],
        mode='lines+markers',
        name=f'Dataset {dataset}'
    ))

# Add the TIN surface using the Delaunay triangles
fig.add_trace(go.Mesh3d(
    x=x_flat,
    y=y_flat,
    z=z_flat,
    i=triangulation.simplices[:, 0],  # Indices of the first vertex of each triangle
    j=triangulation.simplices[:, 1],  # Indices of the second vertex of each triangle
    k=triangulation.simplices[:, 2],  # Indices of the third vertex of each triangle
    opacity=0.6,
    colorscale='Viridis',  # Choose your preferred colorscale
    showscale=True  # Show color scale
))

# Set the ranges for each axis
x_range = [df_combined['X'].min(), df_combined['X'].max()]
y_range = [df_combined['Y'].min(), df_combined['Y'].max()]
z_range = [df_combined['Z'].min(), df_combined['Z'].max()]

# Update layout with axis ranges and other parameters
fig.update_layout(
    scene=dict(
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        zaxis=dict(range=z_range)
    ),
    margin=dict(l=0, r=0, b=0, t=0),
)

fig.show()
