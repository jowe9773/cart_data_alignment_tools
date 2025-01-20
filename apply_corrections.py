#import neccesary modules and packages
import pandas as pd
import math
from pprint import pprint
from functions import FileFunctions

#instantiate classes
ff = FileFunctions()

#load offsets file
offsets_file = ff.load_fn("Choose the offsets excel file", [("Excel Files", "*.xlsx"), ("All Files", "*.*")])

# Load all sheets from the Excel file into a dictionary of DataFrames
autochthonous = pd.read_excel(offsets_file, sheet_name="autochthonous_offsets")

high_pointfive = pd.read_excel(offsets_file, sheet_name="high_0.5")

high_one = pd.read_excel(offsets_file, sheet_name="high_1")

high_two = pd.read_excel(offsets_file, sheet_name="high_2")

high_four = pd.read_excel(offsets_file, sheet_name="high_4")

low_pointfive = pd.read_excel(offsets_file, sheet_name="low_0.5")

low_one = pd.read_excel(offsets_file, sheet_name="low_1")

low_two = pd.read_excel(offsets_file, sheet_name="low_2")

low_four = pd.read_excel(offsets_file, sheet_name="low_4")

all_experiments = [high_pointfive, high_one, high_two, high_four, low_pointfive, low_one, low_two, low_four]

#Iterate through experiments
def identify_scans_that_need_buffer(experiments_df, threshold):
    buffer_list = []
    for index, row in experiments_df.iterrows():
        experiment = row["Experiment"]
        previous_value = row["Previous"]

        if previous_value > threshold:
            nowood = experiment + "_nowood"
            wood = experiment + "_wood"
            buffer_list.append(nowood)
            buffer_list.append(wood)

        if "Remobilization" in experiments_df:
            remobilization_value = row["Remobilization"]
            
            if remobilization_value > threshold:
                remobilization = experiment + "_remobilization"
                buffer_list.append(remobilization)


    return(buffer_list)
            
        
def identify_scans_that_need_realignment(experiments_df, threshold):
    realignment_list = []

    for index, row in experiments_df.iterrows():
        nowood_to_be_realigned = None
        remobilization_to_be_realigned = None
        experiment = row["Experiment"]

        if experiment in experiments_df.columns:  

            nowood_offset = row[experiment]     # Access the value in that column


            if nowood_offset > threshold:
                nowood_to_be_realigned = experiment + "_" + experiment + "_nowood"
                realignment_list.append(nowood_to_be_realigned)


        else:
            # Exclude "Previous" and "Remobilization" columns
            exclude_list = []
            if "Experiment" in experiments_df:
                exclude_list.append("Experiment")
            if "Previous" in experiments_df:
                exclude_list.append("Previous")
            if "Remobilization" in experiments_df:
                exclude_list.append("Remobilization")
            relevant_columns = experiments_df.drop(columns=exclude_list)

 
            min_column = relevant_columns.iloc[index].idxmin()  # Get the column with the lowest value
            min_value = relevant_columns.iloc[index][min_column]  # Get the minimum value itself

            nowood_to_be_realigned = experiment + "_" + min_column + "_nowood"
            realignment_list.append(nowood_to_be_realigned)


        if "Remobilization" in experiments_df:
            remobilization_offset = row["Remobilization"]     # Access the value in that column

            if remobilization_offset > threshold:
                remobilization_to_be_realigned = experiment + "_" + experiment + "_remobilization"
                realignment_list.append(remobilization_to_be_realigned)

    return realignment_list




#select thresholds for alignment
wse_threshold = 2.51
topo_threshold = 1.00

all_exp_realignment_list = []
all_exp_buffer_list = []

for i, dataframe in enumerate(all_experiments):
    buffer_list = identify_scans_that_need_buffer(dataframe, wse_threshold)
    realignment_list = identify_scans_that_need_realignment(dataframe, topo_threshold)

    all_exp_buffer_list.append(buffer_list)
    all_exp_realignment_list.append(realignment_list)

print("Buffer Scans")
pprint(all_exp_buffer_list)

print("Realigment Scans")
pprint(all_exp_realignment_list)
