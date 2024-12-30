#report_offsets_in_topo.py

#The following code will report offsets between different topo scans related to each experiment to find which scans need realignment and which scans can be used as is

# Step 1: Load neccesary modules and packages
import pandas as pd
import os
from scipy.spatial.distance import cdist
from osgeo import gdal
from pprint import pprint
from collections import defaultdict
from functions import FileFunctions, FindPairsFunctions

ff = FileFunctions()
fpf = FindPairsFunctions()


# Step 2: Select Summary File and Directory containing centroid files
summary_file = ff.load_fn("Select a summary file with experiment metadata")

main_directory = ff.load_dn("Choose a directory with all of the centroid filed within it")

# Step 3: Load in summary information
metadata = pd.read_csv(summary_file, usecols= [0,1,2,3])
pprint(metadata)

# Filter out rows with Flood type 'x' or NaN values in Flood type or Experiment Name
filtered_df = metadata[~metadata["Flood type"].isin(['x']) & ~metadata["Forest Stand Density"].isin([1.5]) & metadata["Experiment Name"].notna()]

# Get unique Experiment Names and sort them alphabetically
experiment_names = sorted(filtered_df["Experiment Name"].unique())
pprint(experiment_names)


# Step 4: Parse directory to get all centroid files

# Step 6: Create a list of experiment names in chronological order

# Step 7.1: Create 9 dictionaries (1 for low floods, 4 for high floods, and 4 for autochthonous floods)

# Step 7.2: fill the autochthonous dictionary with key value pairs where the key is the experiment name and the value is a list of all centroid files pertaining to that experiment

# Step 7.3: Fill each high flood dictionary with key value pairs where the key is the experiment name and the value is a list of all centroid files pertaining to that experiment

# Step 7.4: Fill each high flood dictionary with key value pairs where the key is the experiment name and the value is a list of all centroid files pertaining to that experiment

# Step 8.1: Create a function that will add a row to a pandas database containing the median offset magnitude between the pre and post topo scans for a autochthonous experiment

# Step 8.2: Use function to iterate through the autochthonous dictionary to create a pandas database for offset magnitudes for the autochthous experiments and export to a csv.

# Step 9.1: Create a function that will add a row to a pandas database containing the median offset magnitude between the wood topo for an experiment and 1) the previous topo scan and 2) all of the no-wood topo scans from the same relative density

# Step 9.2: Use function to iterate thorugh all four high flood dictionaries to create a pandas database for offset magnitudes for the high flood experiments and export to a csv.

# Step 10.1: Create a function that will add a row to a pandas database containing the median offset magnitude between the wood topo for an experiment and 1) the previous topo scan, 2) the remobilization scan, and 3) all of the no-wood topo scans from the same relative density

# Step 10.2: Use function to iterate thorugh all four high flood dictionaries to create a pandas database for offset magnitudes for the low flood experiments and export to a csv.

