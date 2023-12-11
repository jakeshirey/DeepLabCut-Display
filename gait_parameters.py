from PyQt5.QtWidgets import QDialog, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QCheckBox, QListWidget, QApplication
import pandas as pd
import numpy as np
import scipy.signal

def angle(vertex, point1, point2):
    vertex = np.array(vertex)
    point1 = np.array(point1)
    point2 = np.array(point2)

    vector1 = point1 - vertex
    vector2 = point2 - vertex
    angle = np.arctan2(np.linalg.det([vector1, vector2]), np.dot(vector1, vector2))
    angle = np.degrees(angle)
    return angle

def distance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.linalg.norm(point2 - point1)

def velocity(ds: pd.Series) -> pd.Series:  
    values = ds.to_numpy()
    gradient = np.gradient(values)
    return pd.Series(gradient)

class ParameterInputDialog(QDialog):
    def __init__(self, items, data_frame: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculate Gait Parameters")

        self.items = items
        self.data = data_frame

        self.landmarks = ["Nostril", "Poll", "Withers", "Shoulder", "Elbow", "Mid Back", "Croup", "Hip", 
                          "Stifle", "Dock", "Left Front Hoof", "Left Hind Hoof", "Left Hock", "Left Front Fetlock",
                            "Left Hind Fetlock", "Left Knee", "Right Front Hoof", "Right Hind Hoof", "Right Hock",
                            "Right Front Fetlock", "Right Hind Fetlock", "Right Knee"]

        self.gait_parameters = ["Right Shank", "Left Shank", "Head", "Hind Limb Length", "Hind Leg Length", "Hind Limb Angle", "Fore Limb Angle",
                                "Fore Limb Length", "Fore Leg Length", "Neck Length", "Fore Fetlock Angle", "Hind Fetlock Angle", "Back Angle", "Speed", "Stride Length"]

        self.parameter_inputs = {}
        self.summ_stats_checkbox = None

        self.confirmed_landmarks = {}
        self.summ_stats = []
        self.queried_gait_parameters = []

        layout = QHBoxLayout()
        self.setLayout(layout)

        landmarks_layout = QVBoxLayout()
        landmarks_layout.addWidget(QLabel("Confirm Landmark Points"))
        # Create the sub label inputs
        for landmark in self.landmarks:
            landmark_layout = QHBoxLayout()

            label = QLabel(landmark)
            landmark_layout.addWidget(label)

            combobox = QComboBox()
            combobox.addItems(["Unselected"])
            combobox.addItems(self.items)
            
            self.parameter_inputs[landmark] = combobox
            landmark_layout.addWidget(combobox)

            landmarks_layout.addLayout(landmark_layout)
        layout.addLayout(landmarks_layout)

        gait_params_layout = QVBoxLayout()
        # Gait Parameters label
        gait_parameters_label = QLabel("Choose Gait Parameters")
        gait_params_layout.addWidget(gait_parameters_label)

        # Gait Parameters checklist
        self.gait_parameters_checklist = QListWidget()
        self.gait_parameters_checklist.setSelectionMode(QListWidget.MultiSelection)
        self.gait_parameters_checklist.addItems(self.gait_parameters)
        gait_params_layout.addWidget(self.gait_parameters_checklist)

        layout.addLayout(gait_params_layout)

        # Summary Statistics checkbox
        summ_stats_layout = QHBoxLayout()
        summ_stats_checkbox = QCheckBox()
        self.summ_stats_checkbox = summ_stats_checkbox

        summ_stats_layout.addWidget(summ_stats_checkbox)
        
        summ_stats_label = QLabel("Include Summary Statistics? (Minimum, Maximum, Mean, Standard Deviation)")
        summ_stats_layout.addWidget(summ_stats_label)

        layout.addLayout(summ_stats_layout)

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate_button_clicked)
        layout.addWidget(calculate_button)

    def calculate_button_clicked(self):
        
        for landmark, combobox in self.parameter_inputs.items():
            selected_item = combobox.currentText()
            self.confirmed_landmarks[landmark] = selected_item

        self.queried_gait_parameters = [item.text() for item in self.gait_parameters_checklist.selectedItems()]

        self.summ_stats = self.summ_stats_checkbox.isChecked()

        #print(self.queried_gait_parameters)
        #print(self.confirmed_landmarks)
        #print(self.summ_stats)

        self.perform_calculations()

        self.accept()

    def perform_calculations(self):
        calc_frame = pd.DataFrame(columns=self.queried_gait_parameters, index=self.data.index)

        #DISTANCES
        if "Right Cannon" in self.queried_gait_parameters:
            calc_frame['Right Cannon'] = self.vectorized_distance(column1="Right Hock", column2= "Right Hind Fetlock")
        if "Left Cannon" in self.queried_gait_parameters:
            calc_frame['Left Cannon'] = self.vectorized_distance(column1="Left Hock", column2="Left Hind Fetlock")
        if "Head Length" in self.queried_gait_parameters:
            calc_frame['Head Length'] = self.vectorized_distance("Poll", "Nostril")
        if "Right Hind Croup to Hoof Length" in self.queried_gait_parameters:
            calc_frame['Right Hind Croup to Hoof Length'] = self.vectorized_distance("Croup", "Right Hind Hoof")
        if "Right Hind Cannon Length" in self.queried_gait_parameters:
            calc_frame['Right Hind Cannon Length'] = self.vectorized_distance("Stifle", "Right Hind Fetlock")
        if "Fore Limb Length" in self.queried_gait_parameters:
            calc_frame['Fore Limb Length'] = self.vectorized_distance("Withers", "Right Front Hoof")
        if "Fore Leg Length" in self.queried_gait_parameters:
            calc_frame['Fore Leg Length'] = self.vectorized_distance("Elbow", "Right Front Fetlock")
        if "Neck Length" in self.queried_gait_parameters:
            calc_frame['Neck Length'] = self.vectorized_distance("Poll", "Withers")

        #ANGLES
        if "Hind Fetlock Angle" in self.queried_gait_parameters:
            calc_frame['Hind Fetlock Angle'] = self.vectorized_angle("Right Hind Fetlock", "Right Hind Hoof", "Right Hock")
        if "Fore Fetlock Angle" in self.queried_gait_parameters:
            calc_frame['Fore Fetlock Angle'] = self.vectorized_angle("Right Front Fetlock", "Right Front Hoof", "Right Knee")
        if "Back Angle" in self.queried_gait_parameters:
            calc_frame['Back Angle'] = self.vectorized_angle("Mid Back", "Croup", "Withers")
        if "Hind Limb Angle" in self.queried_gait_parameters:
            calc_frame['Hind Limb Angle'] = self.vectorized_angle("Croup", "Right Hind Hoof", "Croup", isForeHindLimbAngle=True) # pass the vertex in again with flag to create a vertical vector
        if "Fore Limb Angle" in self.queried_gait_parameters:
            calc_frame['Fore Limb Angle'] = self.vectorized_angle("Withers", "Right Front Hoof", "Withers", isForeHindLimbAngle=True)
        
        #SPEED
        if "Speed" in self.queried_gait_parameters:
            calc_frame["Speed"] = self.speed("Withers")
        
        #STRIDE LENGTH
        if "Stride Length" in self.queried_gait_parameters:
            calc_frame["Stride Length"] = self.stride_length("Right Hind Hoof")

        #SUMMARY STATISTICS
        if self.summ_stats:
            # Calculate the statistics (min, max, std, mean) for all columns
            statistics = calc_frame.agg(['min', 'max', 'std', 'mean'])

            # Rename the index to the names of the statistics
            statistics.index = ['Minimum', 'Maximum', 'Standard Deviation', 'Mean']

            # Concatenate the new DataFrame with the original DataFrame and reindex
            calc_frame = pd.concat([statistics, calc_frame])
            
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Gait Parameters to File", '', '*.csv')
        calc_frame.to_csv(save_path)
    
    def vectorized_angle(self, vertex: str, endpoint1: str, endpoint2: str, isForeHindLimbAngle=False):
            '''
            Wrapper function to neatly perform a vectorized angle operation on vertex, endpoint1, and endpoint2. Returns a numpy ndarray.
            '''
            vertexx = self.confirmed_landmarks[vertex] + '_x'
            vertexy = self.confirmed_landmarks[vertex] + '_y'
            endpoint1x = self.confirmed_landmarks[endpoint1] + '_x'
            endpoint1y = self.confirmed_landmarks[endpoint1] + '_y'
            endpoint2x = self.confirmed_landmarks[endpoint2] + '_x'
            endpoint2y = self.confirmed_landmarks[endpoint2] + '_y'
            if isForeHindLimbAngle:
                ep2 = self.data[[endpoint2x, endpoint2y]].values
                ep2[:,1] += 1
            else:
                ep2 = self.data[[endpoint2x, endpoint2y]].values


            return np.vectorize(angle, signature='(n),(n),(n)->()')(self.data[[vertexx, vertexy]].values,
                                                                                self.data[[endpoint1x, endpoint1y]].values,
                                                                                ep2)            

    def vectorized_distance(self, column1: str, column2: str):
            '''
            Wrapper function to neatly perform a vectorized distance operation on column1 and column2. Returns a numpy ndarray.
            '''
            column1x = self.confirmed_landmarks[column1] + '_x'
            column1y = self.confirmed_landmarks[column1] + '_y'
            column2x = self.confirmed_landmarks[column2] + '_x'
            column2y = self.confirmed_landmarks[column2] + '_y'

            return np.vectorize(distance, signature='(n),(n)->()')(self.data[[column1x, column1y]].values, self.data[[column2x, column2y]].values)
    
    def speed(self, column: str):
        '''
        Obtain the speed (horizontal and vertical component) of a point on the body. Units are in pixels/frame.
        '''
        columnx = self.confirmed_landmarks[column] + '_x'
        columny = self.confirmed_landmarks[column] + '_y'  

        horizontal = np.gradient(self.data[columnx].to_numpy()) #since each frame is recorded, we do not need a delta-x step
        vertical = np.gradient(self.data[columnx].to_numpy())

        return np.vectorize(np.linalg.norm, signature='(n)->()')(np.array([horizontal, vertical]).T) #use the pythagorean theorem on both components
    
    def stride_length(self, column: str):
        columnx = self.confirmed_landmarks[column] + '_x'
        self.data[columnx] = scipy.signal.butter(3, 0.05)
        result = scipy.signal.find_peaks_cwt(self.data[columnx].to_numpy(), np.arange(1,5))
        print(result)
        return result
    
#Testing script for widget
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    gui = ParameterInputDialog(items)
    gui.show()

    sys.exit(app.exec_())
