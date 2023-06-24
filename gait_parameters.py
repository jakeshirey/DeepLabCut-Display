from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QDialog, QLabel, QComboBox, QDialogButtonBox, QMessageBox, QLineEdit
from PyQt5.QtGui import QFont
class ParameterInputDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Names")
        self.selected_values = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        labels = [
            ("Left Shank", ["Left Hind Hock", "Left Hind Fetlock"]),
            ("Right Shank", ["Right Hind Hock", "Right Hind Fetlock"]),
            ("Head", ["Poll", "Nostrils"]),
            ("Hind Limb Length", ["Croup", "Right Hind Hoof"]),
            ("Hind Leg Length", ["Stifle", "Right Hind Fetlock"]),
            ("Fore Limb Length", ["Withers", "Right Front Hoof"]),
            ("Fore Leg Length", ["Elbow", "Right Front Fetlock"]),
            ("Neck Length", ["Poll", "Withers"]),
            ("Forelimb Angle", ["Withers", "Right Front Hoof"]),
            ("Hind Limb Angle", ["Croup", "Right Hind Hoof"]),
            ("Fore Fetlock Angle", ["Right Front Fetlock", "Right Front Hoof", "Right Knee"]),
            ("Hind Fetlock Angle", ["Right Hind Fetlock", "Right Hind Hoof", "Right Hock"])
        ]

        for main_label, sub_labels in labels:
            hbox = QHBoxLayout()
            layout.addLayout(hbox)

            main_label_label = QLabel(main_label)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            main_label_label.setFont(font)
            hbox.addWidget(main_label_label)

            for sub_label in sub_labels:
                sub_label_label = QLabel(sub_label)
                hbox.addWidget(sub_label_label)

                combo_box = QComboBox()
                combo_box.addItems(items)
                hbox.addWidget(combo_box)

                self.selected_values[sub_label] = combo_box

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)
        layout.addWidget(calculate_button)

    def calculate(self):
        selected_values = {}
        for sub_label, combo_box in self.selected_values.items():
            selected_values[sub_label] = combo_box.currentText()

        self.selected_values = selected_values
        self.accept()


class MyGUI(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("My GUI")

        self.list_widget1 = QListWidget(self)
        self.list_widget1.addItems(items)

        self.list_widget2 = QListWidget(self)
        self.list_widget2.addItems(items)

        self.button = QPushButton("Select Names", self)
        self.button.clicked.connect(self.handle_button_click)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget1)
        layout.addWidget(self.list_widget2)
        self.setLayout(layout)

    def handle_button_click(self):
        items = [self.list_widget1.item(i).text() for i in range(self.list_widget1.count())]

        if items:
            dialog = ParameterInputDialog(items)
            if dialog.exec_() == QDialog.Accepted:
                selected_values = dialog.selected_values
                print(selected_values)
        else:
            print("The list is empty.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    gui = MyGUI(items)
    gui.show()

    sys.exit(app.exec_())