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
output_directory = ff.load_dn("Choose an output directory")

main_directory = ff.load_dn("Choose a directory with all of the centroid filed within it")

# Load in summary information
metadata = pd.read_csv(summary_file, usecols= [0,1,2,3])


# Filter out rows with Flood type 'x' or NaN values in Flood type or Experiment Name
filtered_df = metadata[~metadata["Flood type"].isin(['x']) & ~metadata["Forest Stand Density"].isin([1.5]) & metadata["Experiment Name"].notna()]

# Get unique Experiment Names and sort them alphabetically
experiment_names = sorted(filtered_df["Experiment Name"].unique())

# find all centroid files in main_directory
centroid_files = ff.find_files_with_string(main_directory, "centroid", ".shp")


#Lets start with autrochthonous experiments, first lets make a dictrionary which will eventually have experiment names for keys and a list of centroid files for values
autoc = {}

#get experiment names for autoc experiments
autoc_df = filtered_df[filtered_df["Flood type"].isin(['A'])]

#fill autoc dict with experiment names
for index, row in autoc_df.iterrows():
    
    autoc_centroid_files = [item for item in centroid_files if row["Experiment Name"] in item]

    autoc[row["Experiment Name"]] = autoc_centroid_files

pprint(autoc)


#add header row to output df
headers = []
headers.append("Experiment")
headers.append("Pre-Post")

output_df = pd.DataFrame(columns = headers)


#Now we have the files that we want to compare, so for each experiment lets comapre the pre and post positions
for key, value in autoc.items():
    for item in value:
        if 'pre' in item:
            pre = item
        elif 'post' in item:
            post = item

    median_direction, median_distance = fpf.find_median_offset_from_scans(pre, post)
    print(key, ": ", median_distance)

    experiment_output = [key, median_distance]
    output_df = pd.concat([output_df, pd.DataFrame([experiment_output], columns = output_df.columns)], ignore_index=True)
    print("Output DF: ", output_df)

    output_filepath = output_directory + "/autochthonous_offsets.csv"

    #export dataframe
    output_df.to_csv(output_filepath, index = False)