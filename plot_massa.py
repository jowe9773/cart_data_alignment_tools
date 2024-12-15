#import neccesary packages and modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly
from functions import FileFunctions


ff = FileFunctions()

# Path to your CSV file"
file_path = ff.load_fn("Select your csv file", [("CSV files", "*.CSV"), ("All Files", "*.*")])
# Skip the first 29 rows, use the 30th row as the header, and then skip the 31st row
df = pd.read_csv(file_path, skiprows=29, usecols=[0, 2, 3, 5], header=None)
df.columns = ['Dataset', 'X', 'Y', 'Z']  # Rename columns for clarity

# Display the first few rows to verify
print(df.head())

# Create a 3D plot
fig = plt.figure(figsize=(10, 8))  # Adjust the figsize (width, height)
ax = fig.add_subplot(111, projection='3d')

# Group by the 'Dataset' column and plot each group
for dataset, group in df.groupby('Dataset'):
    ax.plot(group['X'], group['Y'], group['Z'], label=f'Dataset {dataset}')

# Customize the plot
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')
ax.set_title('3D Line Graph of Datasets')
ax.legend()

# Function to adjust axis aspect ratio
def set_3d_aspect(ax, aspect=(1, 1, 1)):
    """Set 3D plot aspect ratio."""
    x_limits = ax.get_xlim()
    y_limits = ax.get_ylim()
    z_limits = ax.get_zlim()
    
    # Calculate the range of each axis
    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    z_range = z_limits[1] - z_limits[0]
    
    # Apply aspect scaling
    x_center = (x_limits[0] + x_limits[1]) / 2
    y_center = (y_limits[0] + y_limits[1]) / 2
    z_center = (z_limits[0] + z_limits[1]) / 2
    
    max_range = max(x_range * aspect[0], y_range * aspect[1], z_range * aspect[2])

    ax.set_xlim(x_center - max_range / 2, x_center + max_range / 2)
    ax.set_ylim(y_center - max_range / 2, y_center + max_range / 2)
    ax.set_zlim(z_center - max_range / 2, z_center + max_range / 2)

# Set custom aspect ratio (e.g., 2x width, 1x height, 1x depth)
set_3d_aspect(ax, aspect=(1, 1, 1))

# Show the plot
plt.show()