from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QCheckBox, QListWidget, QApplication

class ParameterInputDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculate Gait Parameters")

        self.items = items
        self.landmarks = ["Left Hind Hock", "Left Hind Fetlock", "Right Hind Hock", "Right Hind Fetlock",
                           "Poll", "Nostrils", "Croup", "Right Hind Hoof", "Stifle", "Right Hind Fetlock",
                           "Withers", "Right Front Hoof", "Elbow", "Right Front Fetlock", "Right Front Fetlock",
                           "Right Front Hoof", "Right Knee", "Right Hind Fetlock", "Right Hind Hoof", "Right Hock"]

        self.gait_parameters = ["Right Shank", "Left Shank", "Head", "Hind Limb Length", "Hind Leg Length",
                                "Fore Limb Length", "Fore Leg Length", "Neck Length", "Fore Limb Angle",
                                "Hind Limb Angle", "Fore Fetlock Angle", "Hind Fetlock Angle"]

        self.parameter_inputs = {}
        self.include_checklist = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        landmarks_layout = QVBoxLayout()
        landmarks_layout.addWidget(QLabel("Confirm Landmark Points"))
        # Create the sub label inputs
        for sub_label in self.landmarks:
            sub_label_layout = QHBoxLayout()

            label = QLabel(sub_label)
            sub_label_layout.addWidget(label)

            combobox = QComboBox()
            combobox.addItems(self.items)
            self.parameter_inputs[sub_label] = combobox
            sub_label_layout.addWidget(combobox)

            landmarks_layout.addLayout(sub_label_layout)
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
        landmarks = {}
        for sub_label, combobox in self.parameter_inputs.items():
            selected_item = combobox.currentText()
            landmarks[sub_label] = selected_item

        gait_parameters = [item.text() for item in self.gait_parameters_checklist.selectedItems()]

        summ_stats = [item.text() for item in self.include_checklist.selectedItems()]

        print("Landmarks:", landmarks)
        print("Gait Parameters:", gait_parameters)
        print("Summary Statistics:", summ_stats)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    gui = ParameterInputDialog(items)
    gui.show()

    sys.exit(app.exec_())