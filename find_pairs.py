#This function will find pairs that represent the same feature in the two scans

#load neccesary packages and modules
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import numpy as np
from pprint import pprint
from sklearn.cluster import DBSCAN 
from functions import FileFunctions

ff = FileFunctions()

scan1 = ff.load_fn("select reference scan")
scan2 = ff.load_fn("select a second scan")

shapefile_1 = gpd.read_file(scan1)

shapefile_2 = gpd.read_file(scan2)

# Ensure both shapefiles use the same CRS (Coordinate Reference System)
shapefile_1 = shapefile_1.to_crs(shapefile_2.crs)

# Extract the points (coordinates) from both shapefiles
points_1 = shapefile_1.geometry.apply(lambda x: (x.x, x.y)).tolist()
points_2 = shapefile_2.geometry.apply(lambda x: (x.x, x.y)).tolist()

# Calculate pairwise distances between points from the two shapefiles
distances = cdist(points_1, points_2)

pprint(distances)

# Find the closest point pairs (smallest distances)
closest_pairs = []
for i in range(len(points_1)):
    closest_index = distances[i].argmin()  # Index of the closest point in shapefile_2
    closest_pairs.append((shapefile_1.iloc[i], shapefile_2.iloc[closest_index]))

# Prepare lists to store the x and y offsets
x_offsets = []
y_offsets = []


# Calculate the offsets (x_offset and y_offset) for each pair and store them
for pair in closest_pairs:
    point1 = pair[0].geometry
    point2 = pair[1].geometry
    
    # Calculate the offset (difference) in x and y coordinates
    x_offset = point2.x - point1.x
    y_offset = point2.y - point1.y
    
    x_offsets.append(x_offset)
    y_offsets.append(y_offset)

# Combine the offsets into a 2D array for clustering
offsets = np.array(list(zip(x_offsets, y_offsets)))

# Apply DBSCAN clustering to the offsets
dbscan = DBSCAN(eps=2, min_samples=1000)  # eps is the distance threshold, min_samples is the minimum points to form a cluster
labels_dbscan = dbscan.fit_predict(offsets)

# Visualize the DBSCAN clusters
plt.figure(figsize=(8, 6))

# Plot each point with the cluster label as color
unique_labels = set(labels_dbscan)
for label in unique_labels:
    if label == -1:  # Noise points are labeled as -1
        plt.scatter(offsets[labels_dbscan == label][:, 0], offsets[labels_dbscan == label][:, 1], color='gray', label='Noise')
    else:
        plt.scatter(offsets[labels_dbscan == label][:, 0], offsets[labels_dbscan == label][:, 1], label=f'Cluster {label+1}')

# Set labels and title
plt.xlabel('X Offset')
plt.ylabel('Y Offset')
plt.title('Grouped Offsets by Clustering (DBSCAN)')

# Show legend
plt.legend()

# Show the plot
plt.show()
