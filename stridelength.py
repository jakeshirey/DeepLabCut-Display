import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
import numpy as np
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

        # Design parameters
        filter_order = 3
        cutoff_frequency = 0.05  # Half power frequency in MATLAB

        # Calculate the normalized cutoff frequency for Python
        nyquist_frequency = 0.5  # Nyquist frequency is 0.5 in normalized frequency
        cutoff_frequency_python = cutoff_frequency / nyquist_frequency

        # Design Butterworth lowpass filter coefficients
        b, a = butter(filter_order, cutoff_frequency_python, btype='low', analog=False)

        #filter the right hock x component
        filtered_data = filtfilt(b, a, data_frame["righthock_x"])

        #take the gradient of the filtered data
        hockx_gradient = np.gradient(filtered_data)

        #Peaks of gradient correspond to middle of stride
        peaks, _ = find_peaks(np.abs(hockx_gradient), prominence=1, distance=25)
        
        #Threshold between swing and stance is 0.25 the median peak gradient value
        threshold = 0.25 * np.median(hockx_gradient[peaks])
        
        #Stance is 1, swing is 0
        swing_stance = np.where(hockx_gradient <= threshold, 1, 0)


        swing_stance = pd.Series(swing_stance)  # Convert to a pandas Series
        swing_stance = swing_stance.rolling(window=10, center=True, min_periods=1).median()

        # Convert back to a NumPy array if needed
        swing_stance = swing_stance.to_numpy()
        swing_stance[swing_stance == 0.5] = 0


        toestrike, _ = np.where((hockx_gradient[:-1] > threshold) & (hockx_gradient[1:] <= threshold))[0]

        toeoff, _ = find_peaks(-1 * swing_stance, distance=25, width=10)

        plt.figure(figsize=(10, 6))
        #plt.plot(data_frame.index, data_frame["righthock_x"], label='Original Data')
        #plt.plot(data_frame.index, filtered_data, label=f'Filtered Data (Cutoff Frequency = {cutoff_frequency} Hz)')
        plt.plot(data_frame.index, hockx_gradient, label="Gradient")
        plt.plot(peaks, hockx_gradient[peaks], 'rx', label='Detected Peaks')
        plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold')
        plt.plot(toestrike, hockx_gradient[toestrike], 'bx', label='Toe Strikes')
        plt.plot(toeoff, hockx_gradient[toeoff], 'gx', label='Toeoffs')
        plt.fill_between(data_frame.index, 0, swing_stance, color='lightgray', alpha=0.5)
        plt.title('Butterworth Lowpass Filtered Signal')
        plt.xlabel('Frame')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()