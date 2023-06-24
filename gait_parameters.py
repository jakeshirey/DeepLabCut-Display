from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QDialog, QLabel, QComboBox, QDialogButtonBox, QMessageBox, QLineEdit

class ParameterInputDialog(QDialog):
    def __init__(self, items1, items2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Names")
        self.items1 = items1
        self.items2 = items2
        self.selected_name1 = None
        self.selected_name2 = None
        self.text_input = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.combo1 = QComboBox()
        self.combo1.addItems(items1)
        layout.addWidget(QLabel("Parameter 1:"))
        layout.addWidget(self.combo1)

        self.combo2 = QComboBox()
        self.combo2.addItems(items2)
        layout.addWidget(QLabel("Parameter 2:"))
        layout.addWidget(self.combo2)

        self.text_input = QLineEdit()
        layout.addWidget(QLabel("Enter a Name for the New Parameter"))
        layout.addWidget(self.text_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        self.selected_name1 = self.combo1.currentText()
        self.selected_name2 = self.combo2.currentText()
        self.text_input_value = self.text_input.text()
        super().accept()


class MyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.list_widget1 = QListWidget(self)
        self.list_widget1.addItems(["Name 1", "Name 2", "Name 3"])  # Example names

        self.list_widget2 = QListWidget(self)
        self.list_widget2.addItems(["Name A", "Name B", "Name C"])  # Example names

        self.button = QPushButton("Select Names", self)
        self.button.clicked.connect(self.handle_button_click)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget1)
        layout.addWidget(self.list_widget2)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def handle_button_click(self):
        items1 = [self.list_widget1.item(i).text() for i in range(self.list_widget1.count())]
        items2 = [self.list_widget2.item(i).text() for i in range(self.list_widget2.count())]

        if items1 and items2:
            dialog = ParameterInputDialog(items1, items2)
            if dialog.exec_() == QDialog.Accepted:
                selected_name1 = dialog.selected_name1
                selected_name2 = dialog.selected_name2
                QMessageBox.information(self, "Selected Names", f"Parameter 1: {selected_name1}\nParameter 2: {selected_name2}")
        else:
            QMessageBox.warning(self, "No Names", "The list is empty.")


if __name__ == "__main__":
    app = QApplication([])
    gui = MyGUI()
    gui.show()
    app.exec_()
