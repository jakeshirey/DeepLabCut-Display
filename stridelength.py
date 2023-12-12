'''
Reference File for the stride length and duty factor calculations. Runs as a standalone script, where a DLC excel file is given as a command line argument. Includes matplotlib plots for understanding.
'''
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
        filter_order = 8
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
        
        footstrikes = np.where((hockx_gradient[:-1] >= threshold) & (hockx_gradient[1:] < threshold))[0]

        # Find locations where values rise from below threshold to above
        toeoffs = np.where((hockx_gradient[:-1] < threshold) & (hockx_gradient[1:] >= threshold))[0]

        # Check if any crossings are found
        if toeoffs.size > 0:
            rise_count_threshold = 10
            # Find locations where values rise above the threshold for the tenth time past the intersection
            ten_above = []
            for toeoff in toeoffs:
                if hockx_gradient[toeoff+10] and hockx_gradient[toeoff+10] > threshold:
                    ten_above.append(toeoff+10)
        
        if ten_above:
            toeoffs = ten_above

        strides = [footstrikes[:-1], footstrikes[1:]]
        
        #stride length as distance between start and end of stride
        stride_lengths = strides[1] - strides[0]

        #remove an extra toeoff if one exists before a strike
        if toeoffs[0] < footstrikes[0]:
            toeoffs = toeoffs[1:]
        
        #calculate duty factor for each stride based on start and end of stride, and the toeoff inbetween
        dutyfactor = np.zeros(len(strides[0]))
        for j in range(len(strides[0])):
            stridestart = strides[j][0]
            strideend = strides[j][1]

            strideToeOff = toeoff[toeoff > stridestart]

            # Temporal
            timestance = toeoffs[j] - stridestart
            dutyfactor[j] = timestance / (strideend - stridestart)

        print(strides)
        print(stride_lengths)
        print(dutyfactor)

        plt.figure(figsize=(10, 6))
        #plt.plot(data_frame.index, data_frame["rightHhoof_x"], label='Original Data')
        #plt.plot(data_frame.index, filtered_data, label=f'Filtered Data (Cutoff Frequency = {cutoff_frequency} Hz)')
        plt.plot(data_frame.index, hockx_gradient, label="First")
        plt.plot(peaks, hockx_gradient[peaks], 'rx', label='Detected Peaks')
        plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold')
        plt.plot(footstrikes, hockx_gradient[footstrikes], 'bx', label='Toe Strikes')
        plt.plot(toeoffs, hockx_gradient[toeoffs], 'gx', label='Toeoffs')
        #plt.fill_between(data_frame.index, 0, swing_stance, color='lightgray', alpha=0.5)
        plt.title('Butterworth Lowpass Filtered Signal')
        plt.xlabel('Frame')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()