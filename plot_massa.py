#import neccesary packages and modules
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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
fig = plt.figure()
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

# Show the plot
plt.show()