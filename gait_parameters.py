from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QCheckBox, QListWidget, QApplication
import pandas as pd
import numpy as np

class ParameterInputDialog(QDialog):
    def __init__(self, items, data_frame: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculate Gait Parameters")

        self.items = items
        self.data = data_frame

        self.landmarks = ["Left Hind Hock", "Left Hind Fetlock", "Right Hind Hock", "Right Hind Fetlock",
                           "Poll", "Nostrils", "Croup", "Right Hind Hoof", "Stifle", "Right Hind Fetlock",
                           "Withers", "Right Front Hoof", "Elbow", "Right Front Fetlock", "Right Front Fetlock",
                           "Right Front Hoof", "Right Knee", "Right Hind Fetlock", "Right Hind Hoof", "Right Hock"]

        self.gait_parameters = ["Right Shank", "Left Shank", "Head", "Hind Limb Length", "Hind Leg Length",
                                "Fore Limb Length", "Fore Leg Length", "Neck Length", "Fore Limb Angle",
                                "Hind Limb Angle", "Fore Fetlock Angle", "Hind Fetlock Angle"]

        self.parameter_inputs = {}
        self.include_checklist = None

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

        # Include checklist
        include_layout = QVBoxLayout()
        include_label = QLabel("Include Summary Statistics")
        include_layout.addWidget(include_label)

        include_checklist = QListWidget()
        include_checklist.setSelectionMode(QListWidget.MultiSelection)
        include_checklist.addItems(["Minimum", "Maximum", "Average", "Standard Deviation"])
        self.include_checklist = include_checklist

        include_checklist_layout = QHBoxLayout()
        include_checklist_layout.addStretch()
        include_checklist_layout.addWidget(include_checklist)
        include_checklist_layout.addStretch()

        include_layout.addLayout(include_checklist_layout)

        layout.addLayout(include_layout)

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate_button_clicked)
        layout.addWidget(calculate_button)

    def calculate_button_clicked(self):
        
        for landmark, combobox in self.parameter_inputs.items():
            selected_item = combobox.currentText()
            self.confirmed_landmarks[landmark] = selected_item

        self.queried_gait_parameters = [item.text() for item in self.gait_parameters_checklist.selectedItems()]

        self.summ_stats = [item.text() for item in self.include_checklist.selectedItems()]

        self.perform_calculations()

        self.accept()

    def perform_calculations(self):
        calc_frame = pd.DataFrame(columns=self.queried_gait_parameters, index=self.data.index)

        if "Right Shank" in self.queried_gait_parameters:
            calc_frame['distance'] = np.vectorize(distance)(self.data[[self.confirmed_landmarks['Right Hind Hock'] + '_x', self.confirmed_landmarks['Right Hind Hock'] + '_y']],
                                                            self.data[[self.confirmed_landmarks['Right Hind Fetlock'] + '_x', self.confirmed_landmarks['Right Hind Fetlock'] + '_y']])


        print(calc_frame)

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


#Testing script for widget
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    gui = ParameterInputDialog(items)
    gui.show()

    sys.exit(app.exec_())
