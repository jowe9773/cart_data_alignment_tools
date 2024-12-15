#import neccesary packages and modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from functions import FileFunctions


ff = FileFunctions()

# Path to your CSV file"
file_path = ff.load_fn("Select your csv file", [("CSV files", "*.CSV"), ("All Files", "*.*")])
# Skip the first 29 rows, use the 30th row as the header, and then skip the 31st row
df = pd.read_csv(file_path, skiprows=29, usecols=[0, 2, 3, 5], header=None)
df.columns = ['Dataset', 'X', 'Y', 'Z']  # Rename columns for clarity

#Append data to df from the channel scan
file_path_channel = ff.load_fn("Select your csv file", [("CSV files", "*.CSV"), ("All Files", "*.*")])
df_channel = pd.read_csv(file_path_channel, skiprows=29, usecols=[2, 3, 5], header=None)
df_channel.columns = ['X', 'Y', 'Z']  # Rename columns for clarity
df_channel["Dataset"] = 6

# Display the first few rows to verify
print(df.head())
print(df_channel.head())

df_combined = pd.concat([df, df_channel], ignore_index=True)


# Create a 3D scatter plot
fig = go.Figure()

# Plot each dataset
for dataset, group in df_combined.groupby('Dataset'):
    fig.add_trace(go.Scatter3d(
        x=group['X'],
        y=group['Y'],
        z=group['Z'],
        mode='lines+markers',
        name=f'Dataset {dataset}'
    ))

# Calculate the ranges of each axis
x_range = [df_combined['X'].min(), df_combined['X'].max()]
y_range = [df_combined['Y'].min(), df_combined['Y'].max()]
z_range = [df_combined['Z'].min(), df_combined['Z'].max()]

# Set the axis ranges to be the same proportionally
fig.update_layout(
    scene=dict(
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        zaxis=dict(range=z_range)
    ),
    margin=dict(l=0, r=0, b=0, t=0),  # Optional: remove margins for tight layout
)

fig.show()