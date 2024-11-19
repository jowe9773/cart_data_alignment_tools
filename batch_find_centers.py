#batch_find_centers.py

#load neccesary packages and modules
import os
from functions import FileFunctions
from find_centers import FindCenters

ff = FileFunctions()
fc = FindCenters()


def find_processed_files(root_dir, file_extension):
    matching_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if file.endswith(file_extension):
                # Normalize to consistent forward slashes
                normalized_path = os.path.normpath(file_path).replace("\\", "/")
                matching_files.append(normalized_path)
    return matching_files

#load directory containing all geotiffs
input_directory = ff.load_dn("Select a directory to parse for sick geotiff files")

#select an output directory
output_directory = ff.load_dn("Select a place to store all of the output shapefiles")


extension = ".tif"  # Change to your desired file type
files = find_processed_files(input_directory, extension)

for i, file in enumerate(files):
    fc.find_centers(file, output_directory)