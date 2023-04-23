# gui_qt.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton
from converter import UnitConverter

class UnitConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Unit Converter")
        self.setGeometry(100, 100, 300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.create_widgets()

    def create_widgets(self):
        layout = QGridLayout(self.central_widget)

        self.category_combobox = QComboBox()
        self.category_combobox.addItems(UnitConverter.get_categories())
        self.category_combobox.currentIndexChanged.connect(self.update_units)
        layout.addWidget(QLabel("Category:"), 0, 0)
        layout.addWidget(self.category_combobox, 0, 1)

        self.from_unit_combobox = QComboBox()
        layout.addWidget(QLabel("From Unit:"), 1, 0)
        layout.addWidget(self.from_unit_combobox, 1, 1)

        self.to_unit_combobox = QComboBox()
        layout.addWidget(QLabel("To Unit:"), 2, 0)
        layout.addWidget(self.to_unit_combobox, 2, 1)

        self.value_input = QLineEdit()
        layout.addWidget(QLabel("Value:"), 3, 0)
        layout.addWidget(self.value_input, 3, 1)

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button, 4, 0, 1, 2)

        self.result_label = QLabel("Result:")
        layout.addWidget(self.result_label, 5, 0)
        self.result_value_label = QLabel()
        layout.addWidget(self.result_value_label, 5, 1)

        self.update_units()

    def update_units(self):
        try:
            category = self.category_combobox.currentText()
            units = UnitConverter.get_units(category)
            self.from_unit_combobox.clear()
            self.from_unit_combobox.addItems(units)
            self.to_unit_combobox.clear()
            self.to_unit_combobox.addItems(units)
        except ValueError:
            pass

    def convert(self):
        try:
            value = float(self.value_input.text())
            from_unit = self.from_unit_combobox.currentText()
            to_unit = self.to_unit_combobox.currentText()
            result = UnitConverter.convert(value, from_unit, to_unit)
            self.result_value_label.setText(str(result))
        except ValueError as e:
            self.result_value_label.setText(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = UnitConverterApp()
    mainWin.show()
    sys.exit(app.exec_())
