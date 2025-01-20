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

output_directory = ff.load_dn("Select an output directory")

main_directory = ff.load_dn("Choose a directory with all of the centroid filed within it")

# Load in summary information
metadata = pd.read_csv(summary_file, usecols= [0,1,2,3])


# Filter out rows with Flood type 'x' or NaN values in Flood type or Experiment Name
filtered_df = metadata[~metadata["Flood type"].isin(['x']) & ~metadata["Forest Stand Density"].isin([1.5]) & metadata["Experiment Name"].notna()]

# find all centroid files in main_directory
centroid_files = ff.find_files_with_string(main_directory, "centroid", ".shp")

"""No Wood Scans by FSD"""
#now lets make a list of dictionaries containing all the nowood scans for each forest stand density
all_scans = [{}, {}, {}, {}]

pointfive_df = filtered_df[filtered_df["Forest Stand Density"].isin([0.5])]
one_df = filtered_df[filtered_df["Forest Stand Density"].isin([1.0])]
two_df = filtered_df[filtered_df["Forest Stand Density"].isin([2.0])]
four_df = filtered_df[filtered_df["Forest Stand Density"].isin([4.0])]

dataframes = [pointfive_df, one_df, two_df, four_df]

#fill dictionaries dict with experiment names
for indy, df in enumerate(dataframes):
    #fill autoc dict with experiment names
    for index, row in df.iterrows():
        
        related_centroid_files = [item for item in centroid_files if row["Experiment Name"] in item]

        all_scans[indy][row["Experiment Name"]] = related_centroid_files

#Create lists for each dictionary
pointfive_nowood = [file for file in all_scans[0].values() for file in file if "nowood" in file]
one_nowood = [file for file in all_scans[1].values() for file in file if "nowood" in file]
two_nowood = [file for file in all_scans[2].values() for file in file if "nowood" in file]
four_nowood = [file for file in all_scans[3].values() for file in file if "nowood" in file]

nowood = [pointfive_nowood, one_nowood, two_nowood, four_nowood]

print("Nowood Scans:")
pprint(nowood)

"""Chronological list of all scans"""
all_centroid_files = ff.find_files_with_string(main_directory, "centroid", ".shp")

chronologial_scan_list = ff.sort_scans_chronologically(all_centroid_files)
print("Chronological list of scans:")
pprint(chronologial_scan_list)

"""Autochthonous Scans"""
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
print("Autochthonous Offsets")
pprint(output_df)




"""All high flood scans"""
high = [{}, {}, {}, {}]

#get experiment names for high experiments
high_df = filtered_df[filtered_df["Flood type"].isin(['H'])]

high_pointfive_df = high_df[high_df["Forest Stand Density"].isin([0.5])]
high_one_df = high_df[high_df["Forest Stand Density"].isin([1.0])]
high_two_df = high_df[high_df["Forest Stand Density"].isin([2.0])]
high_four_df = high_df[high_df["Forest Stand Density"].isin([4.0])]

dataframes = [high_pointfive_df, high_one_df, high_two_df, high_four_df]

#fill dictionaries dict with experiment names
for indy, df in enumerate(dataframes):
    #fill autoc dict with experiment names
    for index, row in df.iterrows():
        
        related_centroid_files = [item for item in centroid_files if row["Experiment Name"] in item]

        high[indy][row["Experiment Name"]] = related_centroid_files
print("All high scans:")
pprint(high)


"""Now lets iterate through each high flood experiment find offsets, and add them to a pandas df"""
all_output_dfs = []

for index, dictionary in enumerate(high):
    
    #select the appropriate nowood scans list
    nowood_scans = nowood[index]

    #add header row to output df
    headers = []
    headers.append("Experiment")
    headers.append("Previous")
    for i, file in enumerate(nowood_scans):
        experiment_name = ff.extract_info_from_filename(file)[2]
        headers.append(experiment_name)
    
    output_df = pd.DataFrame(columns = headers)
    print("Dictonary #: ", index)

    for key, value in dictionary.items(): #for each high flood experiment:

        print("Experiment: ", key)

        #find the filename for the wood scan
        target_string = "_wood"
        for item in value:
            if target_string in item:
                wood_scan = item
                break  # Exit the loop after finding the first match

        #find the filename for the previously recorded scan
        for index, item in enumerate(chronologial_scan_list):
            if wood_scan in item:
                previous_scan = chronologial_scan_list[index - 1]
                break  # Exit the loop after finding the first match

        #we are going to find offsets between wood scan and others with the wood scan always in the "scan1" slot

        offset_previous = fpf.find_median_offset_from_scans(wood_scan, previous_scan)[1]

        nowood_offsets = []
        for index, nowood_scan in enumerate(nowood_scans):
            nowood_offset = fpf.find_median_offset_from_scans(wood_scan, nowood_scan)[1]
            nowood_offsets.append(nowood_offset)

        experiment_output = [key, offset_previous] + nowood_offsets

        print(experiment_output)

        output_df = pd.concat([output_df, pd.DataFrame([experiment_output], columns = output_df.columns)], ignore_index=True)

        print("Output DF: ", output_df)

    all_output_dfs.append(output_df)

    print("all output dfs")
    pprint(all_output_dfs)

"""Save each dataframe as a csv file"""
high_csv_filenames = ["high_pointfive_offsets", "high_one_offsets", "high_two_offsets", "high_four_offsets"]

for i, csv in enumerate(high_csv_filenames):
    #create output filepath
    output_filepath = output_directory + "/" + csv + ".csv"

    #export dataframe
    all_output_dfs[i].to_csv(output_filepath, index = False)


'''Now for the low scans'''
low = [{}, {}, {}, {}]

#get experiment names for high experiments
low_df = filtered_df[filtered_df["Flood type"].isin(['L'])]

low_pointfive_df = low_df[low_df["Forest Stand Density"].isin([0.5])]
low_one_df = low_df[low_df["Forest Stand Density"].isin([1.0])]
low_two_df = low_df[low_df["Forest Stand Density"].isin([2.0])]
low_four_df = low_df[low_df["Forest Stand Density"].isin([4.0])]

dataframes = [low_pointfive_df, low_one_df, low_two_df, low_four_df]

#fill dictionaries dict with experiment names
for indy, df in enumerate(dataframes):
    #fill autoc dict with experiment names
    for index, row in df.iterrows():
        
        related_centroid_files = [item for item in centroid_files if row["Experiment Name"] in item]

        low[indy][row["Experiment Name"]] = related_centroid_files
print("All low scans:")
pprint(low)


"""Now lets iterate through each low flood experiment find offsets, and add them to a pandas df"""
all_output_dfs = []

for index, dictionary in enumerate(low):
    
    #select the appropriate nowood scans list
    nowood_scans = nowood[index]

    #add header row to output df
    headers = []
    headers.append("Experiment")
    headers.append("Previous")
    headers.append("Remobilization")
    for i, file in enumerate(nowood_scans):
        experiment_name = ff.extract_info_from_filename(file)[2]
        headers.append(experiment_name)
    
    output_df = pd.DataFrame(columns = headers)
    print("Dictonary #: ", index)

    for key, value in dictionary.items(): #for each high flood experiment:
        remobilization_scan = None
        print("Experiment: ", key)

        #find the filename for the wood scan
        target_string = "_wood"
        for item in value:
            if target_string in item:
                wood_scan = item
                break  # Exit the loop after finding the first match

        
        #find the filename for the previously recorded scan
        for index, item in enumerate(chronologial_scan_list):
            if wood_scan in item:
                previous_scan = chronologial_scan_list[index - 1]
                break  # Exit the loop after finding the first match

        #find the filename for the remobilization scan
        target_string = "_remobilization"
        for item in value:
            if target_string in item:
                remobilization_scan = item
                break  # Exit the loop after finding the first match

        if remobilization_scan == None:
            print(f"No remobilization scan for experiment {key}")

        #we are going to find offsets between wood scan and others with the wood scan always in the "scan1" slot

        offset_previous = fpf.find_median_offset_from_scans(wood_scan, previous_scan)[1]

        offset_remobilization = fpf.find_median_offset_from_scans(wood_scan, remobilization_scan)[1]

        nowood_offsets = []
        for index, nowood_scan in enumerate(nowood_scans):
            nowood_offset = fpf.find_median_offset_from_scans(wood_scan, nowood_scan)[1]
            nowood_offsets.append(nowood_offset)

        experiment_output = [key, offset_previous, offset_remobilization] + nowood_offsets

        print(experiment_output)

        output_df = pd.concat([output_df, pd.DataFrame([experiment_output], columns = output_df.columns)], ignore_index=True)

        print("Output DF: ", output_df)

    all_output_dfs.append(output_df)

    print("all output dfs")
    pprint(all_output_dfs)

"""Save each dataframe as a csv file"""
high_csv_filenames = ["low_pointfive_offsets", "low_one_offsets", "low_two_offsets", "low_four_offsets"]

for i, csv in enumerate(high_csv_filenames):
    #create output filepath
    output_filepath = output_directory + "/" + csv + ".csv"

    #export dataframe
    all_output_dfs[i].to_csv(output_filepath, index = False)
