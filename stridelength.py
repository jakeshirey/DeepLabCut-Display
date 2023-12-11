import pandas as pd
import sys

if __name__ == "__main__":
    # Check if the file name is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python read_excel.py <excel_file_name>")
    else:
        # Get the Excel file name from the command line
        excel_file_name = sys.argv[1]
        data_frame = pd.read_excel(excel_file_name)
        #clean data by combining labels and reindexing
        bodyparts_labels = data_frame.loc[0]
        coords_labels = data_frame.loc[1]
        labels = [i + "_" + j for i, j in zip(bodyparts_labels, coords_labels)]
        data_frame.columns = labels
        data_frame = data_frame.iloc[2: , : ]
        data_frame.index = range(len(data_frame.index))
        data_frame = data_frame.drop(columns=["bodyparts_coords"])
        print(data_frame)

        