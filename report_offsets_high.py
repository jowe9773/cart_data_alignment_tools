#report_offsets_autoc.py

# The following code will report offsets between different topo scans related to each experiment to find which scans need realignment and which scans can be used as is

# Load neccesary modules and packages
import pandas as pd
from pprint import pprint
from functions import FileFunctions, FindPairsFunctions

ff = FileFunctions()
fpf = FindPairsFunctions()


# Select Summary File and Directory containing centroid files
summary_file = ff.load_fn("Select a summary file with experiment metadata")

main_directory = ff.load_dn("Choose a directory with all of the centroid filed within it")

# Load in summary information
metadata = pd.read_csv(summary_file, usecols= [0,1,2,3])


# Filter out rows with Flood type 'x' or NaN values in Flood type or Experiment Name
filtered_df = metadata[~metadata["Flood type"].isin(['x']) & ~metadata["Forest Stand Density"].isin([1.5]) & metadata["Experiment Name"].notna()]

# Get unique Experiment Names and sort them alphabetically
experiment_names = sorted(filtered_df["Experiment Name"].unique())

# find all centroid files in main_directory
centroid_files = ff.find_files_with_string(main_directory, "centroid", ".shp")

pointfive = {}
one = {}
two = {}
four = {}

high = [pointfive, one, two, four]
pprint(high)

#get experiment names for high experiments
high_df = filtered_df[filtered_df["Flood type"].isin(['H'])]

pointfive_df = high_df[high_df["Forest Stand Density"].isin([0.5])]
one_df = high_df[high_df["Forest Stand Density"].isin([1.0])]
two_df = high_df[high_df["Forest Stand Density"].isin([2.0])]
four_df = high_df[high_df["Forest Stand Density"].isin([4.0])]

dataframes = [pointfive_df, one_df, two_df, four_df]

#fill dictionaries dict with experiment names
for indy, df in enumerate(dataframes):
    #fill autoc dict with experiment names
    for index, row in df.iterrows():
        
        related_centroid_files = [item for item in centroid_files if row["Experiment Name"] in item]

        high[indy][row["Experiment Name"]] = related_centroid_files

pprint(high)
        
