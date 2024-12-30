# Import necessary libraries
import pandas as pd
import os
from scipy.spatial.distance import cdist
from osgeo import gdal
from pprint import pprint
from collections import defaultdict
from functions import FileFunctions
from functions import FindPairsFunctions

# Initialize FileFunctions for file selection
ff = FileFunctions()
fpf = FindPairsFunctions()

# Step 1: Choose a directory where centroid files can be found
main_directory = ff.load_dn("Select Directory Containing Centroid files")

# Step 2: Find all centroid files in the directory
shp_files = ff.find_files_with_string(main_directory, "centroids", ".shp")

#group centroid files by experiment
experiment_dict = defaultdict(list)

for filepath in shp_files:
    _, _, exp = ff.extract_info_from_filename(filepath)  # Use your function to extract the experiment name
    experiment_dict[exp].append(filepath)

pprint(experiment_dict)

# Prepare an output pandas dataframe
output_df = pd.DataFrame(columns = ["Experiment", "Scan", "Median Magnitude (mm)", "Median Direction (deg)"])

#Go through each experiment and find median offset magnitude. Use nowood as reference. If no nowood scan then use wood as reference.
priority_keywords = ["_nowood", "_wood", "_re", "_pre", "_post"]

# Iterate through the dictionary and select the reference file
for experiment, files in experiment_dict.items():
    reference = None
    
    for keyword in priority_keywords:
        # Look for a file with the current keyword in its basename
        reference = next((file for file in files if keyword in os.path.basename(file)), None)
        if reference:
            break  # Stop searching if a match is found
    
    #now use the reference file to calculate offset magnitude for each scan
    for file in files:
        if reference is not None:
            #extract info about scan (which experiment and which scan)
            _, basename, exp = ff.extract_info_from_filename(file)

            #find closest pairs in data
            pairs = fpf.find_closest_pairs(reference, file)

            # Calculate offsets
            offsets = fpf.calculate_offsets(pairs)

            # Select "real" offsets using thresholding
            filtered_offsets = fpf.select_true_offsets(offsets, low_threshold= 0, high_threshold= 20)

            # Show filtered offsets
            #fpf.display_offsets(filtered_offsets)

            # Find the median offset angle and magnitude
            median_direction, median_magnitude = fpf.compute_median_direction_and_distance(offsets)

            #add all this scan infomation to the output dataframe
            output_df.loc[len(output_df)] = {"Experiment" : exp, "Scan": basename, "Median Magnitude (mm)": median_magnitude, "Median Direction (deg)": median_direction}

pprint(output_df)

# Save DataFrame to a CSV file
output_df.to_csv('output_file.csv', index=False)